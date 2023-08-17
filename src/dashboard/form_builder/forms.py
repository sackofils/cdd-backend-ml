from django import forms
from django.utils.translation import gettext_lazy as _
from no_sql_client import NoSQLClient
from process_manager.enums import FieldTypeEnum
from process_manager.models import FormField, FormType, Task
from django.apps import apps
from django.forms.models import inlineformset_factory


class FormTypeForm(forms.ModelForm):
    error_messages = {
        "duplicate_field": _("Another field with the same name is already defined"),
        "duplicate_form": _("Another form associated with the task is already defined")
    }
    name = forms.CharField(max_length=140, help_text=_("Unique name for the Model"))
    description = forms.Textarea()  # help_text=_("Description of the form")) #help_text=_("Description of the form"))

    # couch_id = forms.CharField(required=False, disabled=True, help_text=_("Unique name for the Model"))

    def __init__(self, *args, **kwargs):
        """
		@TODO. Get List of models from couch_db. For the selected model, get its instances from couch db
		For this project, just limit model to Task, but this can be applied generically to any model
		"""
        super().__init__(*args, **kwargs)

    # nsc = NoSQLClient()
    # # Get Models
    # MODELS = []
    # app_models = apps.get_models()
    # for m in app_models:
    # 	if m.__name__ == "Task":
    # 		MODELS.append((m.__name__, m.__name__))

    # self.fields['content_type'].choices = MODELS
    # # Get tasks
    # tasks = Task.objects.all()
    # TASKS = []
    # for t in tasks:
    # 	TASKS.append((t.id, t.name))
    # self.fields['content_object'].choices = TASKS

    class Meta:
        model = FormType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'description': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'couch_id': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'readonly': 'True'
                }
            )
        }


class UpdateFormTypeForm(forms.ModelForm):
    name = forms.CharField(help_text=_("Name of the form"))
    description = forms.CharField(help_text=_("Description of the form"))

    # couch_id = forms.CharField(required=False)

    def clean(self):
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = FormType
        fields = ['name', 'description']


class FormFieldForm(forms.ModelForm):
    class Meta:
        FIELD_TYPES = []
        for itm in FieldTypeEnum:
            FIELD_TYPES.append((itm.value, itm.value))

        model = FormField
        fields = ['label', 'field_type', 'name', 'required', 'options', 'help_text', 'page']
        widgets = {
            'label': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'field_type': forms.Select(
                attrs={
                    'class': 'form-control'
                },
                choices=FIELD_TYPES
            ),
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                },
            ),
            'options': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 1,
                    'cols': 3
                }
            ),
            # 'default': forms.Textarea(
            # 	attrs={
            # 		'class': 'form-control'
            # 	}
            # ),
            'required': forms.CheckboxInput(
                attrs={
                    'class': 'text-hide icheck-primary'
                }
            ),
            # 'idx': forms.NumberInput(
            # 	attrs={
            # 		'display': 'hidden'
            # 	}
            # ),
            'page': forms.NumberInput(
                # attrs={
                # 	'class': 'text-hide'
                # }
            ),
            'help_text': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            # 'hidden': forms.BooleanField(
            # 	# attrs={
            # 	# 	'class': 'form-control'
            # 	# }
            # ),
            # 'read_only': forms.BooleanField(
            # 	# attrs={
            # 	# 	'class': 'form-control'
            # 	# }
            # ),
        }


FormFieldFormSet = inlineformset_factory(
    FormType, FormField, form=FormFieldForm,
    extra=1, can_delete=True, can_delete_extra=True
)
# ImageFormSet = inlineformset_factory(
#     Product, Image, form=ImageForm,
#     extra=1, can_delete=True, can_delete_extra=True
# )