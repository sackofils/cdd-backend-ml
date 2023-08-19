from django import forms
from django.utils.translation import gettext_lazy as _
from process_manager.enums import FieldTypeEnum
from process_manager.models import AttachmentType
from django.apps import apps
from dashboard.attachment_type import FILE_TYPES


class AttachmentTypeForm(forms.ModelForm):
    error_messages = {
        "duplicate_attachment_type": _("Another attachment type with the same name is already defined"),
    }

    name = forms.CharField(label=_('Name'), help_text=_('Name of the attachment type'))
    # file_type = forms.CharField(label=_('File type'), help_text=_('Type of the attachment: image or document'))
    # order = forms.IntegerField(label=_('Order'), help_text=_('The order number of the attachment'))

    def clean_name(self):
        name = self.cleaned_data['name']
        if AttachmentType.objects.filter(name=name).exists():
            self.add_error('name', self.error_messages["duplicate_attachment_type"])
        return name

    class Meta:
        model = AttachmentType
        fields = ['name', 'file_type']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'file_type': forms.Select(
                attrs={
                    'class': 'form-control'
                },
                choices=FILE_TYPES
            )
        }


class UpdateAttachmentTypeForm(forms.ModelForm):
    name = forms.CharField(label=_('Name'), help_text=_('Name of the attachment type'))
    # file_type = forms.CharField(label=_('File type'), help_text=_('Type of the attachment: image or document'))
    # order = forms.IntegerField(label=_('Order'), help_text=_('The order number of the attachment'))

    def clean(self):
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = AttachmentType
        fields = ['name', 'file_type']
