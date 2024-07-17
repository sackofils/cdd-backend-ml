from django import forms
from django.utils.translation import gettext_lazy as _
from process_manager.enums import FieldTypeEnum
from authentication.models import OrganismType
from django.apps import apps


class OrganismTypeForm(forms.ModelForm):
    error_messages = {
        "duplicate_organism_type": _("This organism type name already exist."),
    }

    def clean_label(self):
        label = self.cleaned_data['label']
        if OrganismType.objects.filter(label=label).exists():
            self.add_error('label', self.error_messages["duplicate_organism_type"])
        return label

    class Meta:
        model = OrganismType
        fields = ['label', 'description']
        widgets = {
            'label': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'rows': 5,
                    'class': 'form-control'
                }
            )
        }


class UpdateOrganismTypeForm(forms.ModelForm):

    def clean(self):
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = OrganismType
        fields = ['label', 'description']
