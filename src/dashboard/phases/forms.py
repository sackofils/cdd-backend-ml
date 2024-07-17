from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from process_manager.models import Phase, Project
from no_sql_client import NoSQLClient


class PhaseForm(forms.ModelForm):
    error_messages = {
        'duplicated_phase': _('A phase with this name is already registered.'),
    }

    def _post_clean(self):
        super()._post_clean()

    def clean_name(self):
        name = self.cleaned_data['name']
        if Phase.objects.filter(name=name).exists():
            self.add_error('name', self.error_messages["duplicated_phase"])
        return name

    def clean(self):
        return super().clean()

    class Meta:
        model = Phase
        fields = ['name', 'description']  # specify the fields to be displayed


class UpdatePhaseForm(forms.ModelForm):
    def clean(self):
        return super().clean()

    class Meta:
        model = Phase
        fields = ['name', 'description']  # specify the fields to be displayed
