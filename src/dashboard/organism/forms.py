from django import forms
from django.utils.translation import gettext_lazy as _
from process_manager.enums import FieldTypeEnum
from authentication.models import OrganismType, Organism
from django.apps import apps


class OrganismForm(forms.ModelForm):
    error_messages = {
        "duplicate_organism": _("This organism name already exist."),
    }

    def clean_name(self):
        name = self.cleaned_data['name']
        if Organism.objects.filter(name=name).exists():
            self.add_error('name', self.error_messages["duplicate_organism"])
        return name

    class Meta:
        model = Organism
        fields = ['type', 'name', 'acronym', 'email', 'phone', 'address']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'acronym': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 5,'class': 'form-control'})
        }


class UpdateOrganismForm(forms.ModelForm):

    def clean(self):
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Organism
        fields = ['type', 'name', 'acronym', 'email', 'phone', 'address']
