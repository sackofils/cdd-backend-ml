from django.db import models
from no_sql_client import NoSQLClient
from django.utils.translation import gettext_lazy as _
from process_manager.enums import FieldTypeEnum
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from rest_framework import serializers
from dashboard.attachment_type import FILE_TYPES
from collections import defaultdict


# Create your models here.
# The project object on couch looks like this
# {
#     "_id": "219e50bc41c65648039b08eb10e7b925",
#     "_rev": "1-2851220dbb9d42ee9a7d1f2889cf4f83",
#     "type": "project",
#     "name": "COSO",
#     "description": "Lorem ipsum"
# }
class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    order = models.IntegerField()
    couch_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        data = {
            "name": self.name,
            "type": "project",
            "order": self.order,
            "description": self.description,
            "capacity_attachments": [],
            "sql_id": self.id
        }
        nsc = NoSQLClient()
        nsc_database = nsc.get_db("process_design")
        new_document = nsc_database.get_query_result(
            {"_id": self.couch_id}
        )[0]
        if not new_document:
            new_document = nsc.create_document(nsc_database, data)
            self.couch_id = new_document['_id']
            self.save()
        return self

    def simple_save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


# The Phase object on couch looks like this
# {
#     "_id": "abc123",
#     "_rev": "2-ae3f90c1f84c91ff97a4bffd5686a9b7",
#     "type": "phase",
#     "project_id": "219e50bc41c65648039b08eb10e7b925",
#     "administrative_level_id": "adml123", NO
#     "name": "Community Mobilization",
#     "order": 1,
#     "description": "Lorem ipsum",
#     "capacity_attachments": [
#         {
#             "name": "tutorial.pdf",
#             "url": "/attachments/1253a3516c4e88550768d719be04e43d/report.pdf",
#             "bd_id": "1253a3516c4e88550768d719be04e43d"
#         }
#     ]
# }
class Phase(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    total_activities = models.IntegerField(default=0)
    couch_id = models.CharField(max_length=255, blank=True)
    order = models.IntegerField()
    form_type = models.ForeignKey("FormType", on_delete=models.CASCADE, blank=False, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        form_fields = self.form_type.json_schema if self.form_type else None
        data = {
            "name": self.name,
            "type": "phase",
            "description": self.description,
            "order": self.order,
            "capacity_attachments": [],
            "support_attachments": False,
            "total_activities": self.total_activities,
            "project_id": self.project.couch_id,
            "sql_id": self.id,
            "form": form_fields
        }
        nsc = NoSQLClient()
        nsc_database = nsc.get_db("process_design")
        new_document = nsc_database.get_query_result(
            {"_id": self.couch_id}
        )[0]
        if not new_document:
            new_document = nsc.create_document(nsc_database, data)
            self.couch_id = new_document['_id']
            self.save()
        return self

    def simple_save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


# The activity object on couch looks like this
# {
#     "_id": "219e50bc41c65648039b08eb10032af1",
#     "_rev": "357-8cacccf0cbd94ecbaf2f45242a946eb0",
#     "type": "activity",
#     "project_id": "219e50bc41c65648039b08eb10e7b925",
#     "phase_id": "abc123",
#     "administrative_level_id": "adml123",
#     "name": "Réunion cantonale",
#     "order": 1,
#     "description": "Participer à la réunion cantonale conduite par l’AADB",
#     "attachments": [
#         {
#             "name": "tutorial.pdf",
#             "url": "/attachments/1253a3516c4e88550768d719be04e43d/report.pdf",
#             "bd_id": "1253a3516c4e88550768d719be04e43d"
#         }
#     ],
#     "total_tasks": 4,
#     "completed_tasks": 0
# }
class Activity(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    phase = models.ForeignKey("Phase", on_delete=models.CASCADE)
    total_tasks = models.IntegerField()
    order = models.IntegerField()
    couch_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.phase.name + '-' + self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        data = {
            "name": self.name,
            "type": "activity",
            "description": self.description,
            "order": self.order,
            "capacity_attachments": [],
            "support_attachments": False,
            "project_id": self.phase.project.couch_id,
            "phase_id": self.phase.couch_id,
            "total_tasks": self.total_tasks,
            "completed_tasks": 0,
            "sql_id": self.id
        }

        nsc = NoSQLClient()
        nsc_database = nsc.get_db("process_design")
        new_document = nsc_database.get_query_result(
            {"_id": self.couch_id}
        )[0]
        if not new_document:
            new_document = nsc.create_document(nsc_database, data)
            self.couch_id = new_document['_id']

            phase = Phase.objects.get(id=self.phase_id)
            phase.total_activities = Activity.objects.filter(phase_id=phase.id).all().count()
            phase.save()
            docu = {
                "total_activities": phase.total_activities
            }
            query_result = nsc_database.get_query_result({"_id": self.phase.couch_id})[:]
            doc = nsc_database[query_result[0]['_id']]
            nsc.update_doc(nsc_database, doc['_id'], docu)

            self.save()
        return self


# The task object on couch looks like this
# {
#   "_id": "d50db81ec709d67e3b1b299ba60f2666",
#   "_rev": "28-837510813494bd487a329b9d66e693f6",
#   "type": "task",
#   "project_id": "219e50bc41c65648039b08eb10e7b925",
#   "phase_id": "abc123",
#   "phase_name": "VISITES PREALABLES",
#   "activity_id": "219e50bc41c65648039b08eb10032af1",
#   "activity_name": "Réunion cantonale",
#   "administrative_level_id": "adml123",
#   "administrative_level_name": "Sanloaga",
#   "name": "Tarea 2",
#   "order": 2,
#   "description": "Lorem ipsum https://ee.kobotoolbox.org/x/HY43dHN4",
#   "completed": false,
#   "completed_date": "15-08-2022",
#   "capacity_attachments": [],
#   "attachments": [],
#   "form": []
class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    phase = models.ForeignKey("Phase", on_delete=models.CASCADE)
    activity = models.ForeignKey("Activity", on_delete=models.CASCADE)
    order = models.IntegerField()
    duration = models.IntegerField(default=1, help_text=_('Duration in hour'))
    form = models.JSONField(null=True, blank=True)
    couch_id = models.CharField(max_length=255, blank=True)
    form_type = models.ForeignKey("FormType", on_delete=models.CASCADE, blank=False, null=True)
    attachments_json = models.JSONField(null=True, blank=True)
    attachments = models.ManyToManyField("AttachmentType")

    def __str__(self):
        return self.phase.name + '-' + self.activity.name + '-' + self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # form = []
        # if self.form:
        # 	form = self.form
        form_fields = self.form_type.json_schema if self.form_type else None
        attachments_json = [attachment.json_schema for attachment in self.attachments.all()] if self.attachments.all() else []

        # Ordered attachments list
        attachments = []
        index = 0
        for attachment in attachments_json:
            attachment['order'] = index
            attachments.append(attachment)
            index += 1
        print("attachments", attachments)

        print('---')
        # print(self.form_type)
        # print(self.form_type.json_schema)
        data = {
            "type": "task",
            "project_id": self.activity.phase.project.couch_id,
            "phase_id": self.activity.phase.couch_id,
            "phase_name": self.activity.phase.name,
            "activity_id": self.activity.couch_id,
            "activity_name": self.activity.name,
            "name": self.name,
            "order": self.order,
            "description": self.description,
            "completed": False,
            "completed_date": "",
            "capacity_attachments": [],
            "support_attachments": True if len(attachments) > 0 else False,
            "attachments": attachments,
            "form": form_fields,
            "form_response": [],
            "sql_id": self.id
        }
        nsc = NoSQLClient()
        nsc_database = nsc.get_db("process_design")
        new_document = nsc_database.get_query_result(
            {"_id": self.couch_id}
        )[0]
        if not new_document:
            new_document = nsc.create_document(nsc_database, data)
            self.couch_id = new_document['_id']
            activity = Activity.objects.get(id=self.activity_id)
            activity.total_tasks = Task.objects.filter(activity_id=activity.id).all().count()
            activity.save()
            docu = {
                "total_tasks": activity.total_tasks
            }
            query_result = nsc_database.get_query_result({"_id": self.activity.couch_id})[:]
            doc = nsc_database[query_result[0]['_id']]
            nsc.update_doc(nsc_database, doc['_id'], docu)
            self.save()
        return self

    def is_attachments_exist(self):
        is_provided = True
        for attachment in self.attachments:
            if attachment.attachment is None:
                is_provided = False
                break
        return is_provided

    is_attachments_provided = property(is_attachments_exist)


User = get_user_model()


class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT,
                                   related_name="%(app_label)s_%(class)s_creator")
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT,
                                   related_name="%(app_label)s_%(class)s_updater")

    # is_deleted = models.Boolean(default=False)
    # deleted_on = models.DateTimeField(null=True)
    # deleted_by = models.ForeignKey(get_user_model(), null=True)
    class Meta:
        abstract = True

    @classmethod
    def get_serializer(cls):
        class BaseSerializer(serializers.ModelSerializer):
            class Meta:
                model = cls  # tell the serializer about the model class
                exclude = []

        return BaseSerializer  # return the class object so we can use this serializer

    def to_dict(cls, exclude_fields=[]):
        """Return a dict representation of a model

		Args:
			exclude_fields (list, optional): List of fields to be excluded from the dict. Defaults to [].

		Returns:
			dict: Dictionary of the model
		"""
        serializer_class = cls.get_serializer()
        serializer_class.Meta.exclude = exclude_fields
        return serializer_class(cls).data


# Create your models here.
class FormType(BaseModel):
    """
	Model representing a Form
	"""
    name = models.CharField(blank=False, null=False, max_length=140, help_text=_("Unique name for the Model"))
    description = models.TextField(blank=True, null=True, help_text=_("Description of the form"))
    couch_id = models.CharField(blank=True, null=True, max_length=140, help_text=_("Related Couchdb id"))

    def __str__(self):
        return "{0}".format(self.name)

    def _get_json_data(self):
        """Get JSON Format of fields
		https://stackoverflow.com/questions/3535977/can-model-properties-be-displayed-in-a-template

		Returns:
			str: String dictionary representation of the model
		"""
        # get FormFields linked to the Form
        fields = FormField.objects.filter(form=self)
        dct = []
        delete_keys = ['created_by', 'updated_by']
        for fld in fields:
            dct.append(fld.to_dict(exclude_fields=delete_keys))
        return str(dct)

    def _get_json_schema(self):
        """Get JSON schema representation of the FormField
		See https://www.npmjs.com/package/tcomb-json-schema
			https://gcanti.github.io/resources/json-schema-to-tcomb/playground/playground.html
		"""
        type_mapping = {
            FieldTypeEnum.DATA.value: "string",
            FieldTypeEnum.CHECK.value: "boolean",
            FieldTypeEnum.FLOAT.value: "number",
            FieldTypeEnum.INT.value: "number",
            FieldTypeEnum.SMALL_TEXT.value: "string",
            FieldTypeEnum.TEXT.value: "string",
            FieldTypeEnum.SELECT.value: "string",
        }
        fields = FormField.objects.filter(form=self)

        groups = defaultdict(list)
        for obj in fields:
            groups[obj.page].append(obj)

        fields = groups.values()
        dct = {
            "page": {
                "type": "object",
                "properties": {},
                "required": []
            },
            "options": {
                "fields": {}
            }
        }
        result = []
        for group in fields:
            for fld in group:
                # if fld.field_type == FieldTypeEnum.PAGE_BREAK.value:
                # 	"""@TODO. Handle paging"""
                # 	continue
                dct["options"]["fields"][fld.name] = {
                    "label": fld.label,
                    "help": fld.help_text or "",
                    "i18n": {
                        "optional": "",
                        "required": "*"
                    }
                }

                if fld.field_type == FieldTypeEnum.SELECT.value:
                    # For select fields, populate options
                    dct["page"]["properties"][fld.name] = {
                        "type": type_mapping[fld.field_type],
                        "enum": fld.options.splitlines()
                    }
                else:
                    dct["page"]["properties"][fld.name] = {
                        "type": type_mapping[fld.field_type]
                    }

                if fld.required:
                    dct["page"]["required"].append(fld.name)
            result.append(dct)
        return result

    json_schema = property(_get_json_schema)
    json_data = property(_get_json_data)


class FormField(BaseModel):
    """
	Model representing a column/field in a FormType
	"""
    FIELD_TYPES = []
    for itm in FieldTypeEnum:
        FIELD_TYPES.append((itm.value, itm.value))

    form = models.ForeignKey(FormType, on_delete=models.CASCADE)
    name = models.CharField(blank=False, null=False, max_length=140, help_text=_("Unique identifier for the field"))
    label = models.CharField(blank=False, null=False, max_length=140, help_text=_("Field Label"))
    field_type = models.CharField(blank=False, null=False, max_length=140, choices=FIELD_TYPES,
                                  help_text=_("Type of field"))
    # default = models.TextField(help_text=_("Default value for the field"))
    help_text = models.CharField(max_length=255, blank=True, null=True, help_text=_("Text to be displayed as help"))
    required = models.BooleanField(help_text=_("Is the field mandatory"))
    options = models.TextField(blank=True, null=True,
                               help_text=_("For Select, enter list of Options, each on a new line."))
    idx = models.PositiveSmallIntegerField(blank=False, default=1, help_text=_("Order in form"))
    page = models.PositiveSmallIntegerField(blank=False, default=1, help_text=_("Page to appear in form"))

    # hidden = models.BooleanField(help_text=_("Is the field hidden?"))
    # read_only = models.BooleanField(help_text=_("Is the field read-only?"))

    class Meta:
        ordering = ["idx"]


class AttachmentType(BaseModel):
    """ Model representing an Attachment """
    name = models.CharField(blank=False, null=False, max_length=140, help_text=_("Unique name for the Attachment"))
    file_type = models.CharField(blank=False, null=False, max_length=256, choices=FILE_TYPES)
    order = models.IntegerField(default=0)

    def __str__(self):
        return "{0}".format(self.name)

    def _get_json_schema(self):
        file_type = 'image/*'
        if self.file_type == 'Document':
            file_type = 'application/*'

        dct = {
            "attachment": None,
            "name": f"{self.name}",
            "type": f"{file_type}",
            "order": self.order
        }
        return dct

    json_schema = property(_get_json_schema)