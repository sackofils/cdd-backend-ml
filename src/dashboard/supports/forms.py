from django import forms
from django.utils.translation import gettext_lazy as _
from no_sql_client import NoSQLClient


class SupportForm(forms.Form):
    error_messages = {
        'duplicated_support': _('A support with this name is already registered.'),
    }

    name = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    file = forms.FileField()

    def _post_clean(self):
        super()._post_clean()

    def clean_name(self):
        name = self.cleaned_data['name']
        nsc = NoSQLClient()
        db = nsc.get_db('supports')
        query_result = db.get_query_result({"name": name})[:]
        if len(query_result) > 0:
            self.add_error('name', self.error_messages["duplicated_support"])
        return name

    def clean(self):
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UpdateSupportForm(forms.Form):
    name = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    file = forms.FileField(required=False)

    def _post_clean(self):
        super()._post_clean()

    def clean(self):
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
