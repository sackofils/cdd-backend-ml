from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from process_manager.models import Phase, Project, Activity, Task, FormType, AttachmentType
from no_sql_client import NoSQLClient

class TaskForm(forms.Form):
    error_messages = {
        'duplicated_task': _('An Task with this name is already registered.'),
    }
    #choices = tuple(Project.objects.all().values_list())
    name = forms.CharField()
    description = forms.CharField()
    #project = forms.ChoiceField(choices = [])
    #activity = forms.ChoiceField(choices = [])
    #order = forms.IntegerField()
    #form = forms.JSONField(required=False)
    form_type = forms.ModelChoiceField(label=_("Form"), queryset=FormType.objects.distinct())
    attachments = forms.ModelMultipleChoiceField(label=_("Attachments"), queryset=AttachmentType.objects.distinct())

    def _post_clean(self):
        super()._post_clean()

    def clean_name(self):
        name = self.cleaned_data['name']
        if Task.objects.filter(name=name).exists():
            self.add_error('name', self.error_messages["duplicated_task"])
        return name

    def clean(self):
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['project'].choices = [(x.id, x.name) for x in Project.objects.all()]
        #self.fields['activity'].choices = [(p.id, p.name) for p in Activity.objects.all()]

class UpdateTaskForm(forms.ModelForm):
    #choices = tuple(Project.objects.all().values_list())
    name = forms.CharField()
    description = forms.CharField()
    #couch_id = forms.CharField(required=False, disabled=True)
    #activity = forms.ModelChoiceField(queryset=Activity.objects.distinct())
    #form = forms.JSONField(required=False)
    #order = forms.IntegerField()
    form_type = forms.ModelChoiceField(label=_("Form"), queryset=FormType.objects.distinct())
    attachments = forms.ModelMultipleChoiceField(label=_("Attachments"), queryset=AttachmentType.objects.distinct())

    def clean(self):
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['project'].queryset = [(x, x.name) for x in Project.objects.list()]

    class Meta:
        model = Task
        fields = ['name', 'description', 'form_type', 'attachments'] # specify the fields to be displayed