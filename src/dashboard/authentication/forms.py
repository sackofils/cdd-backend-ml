from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext as _
from django import forms

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from authentication.models import Profile, Organism


class EmailAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _('Email')

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        user = User.objects.filter(email__iexact=email).first()

        if not user:
            raise self.get_invalid_login_error()
        if email and password:
            self.user_cache = authenticate(self.request, username=user.username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class CreateUserForm(UserCreationForm):
    organism = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["organism"].choices = ((x, x) for x in Organism.objects.all())

    class Meta:
        """docstring for Meta"""
        model = User
        fields = (
            'username', 'password1', 'password2', 'last_name', 'first_name', 'email',
            'is_superuser', 'is_staff', 'is_active', 'groups'
        )


class UpdateUserForm(forms.ModelForm):
    organism = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["organism"].choices = ((x, x) for x in Organism.objects.all())
        if self.instance.user_profile.organism:
            self.fields["organism"].initial = self.instance.user_profile.organism

    class Meta:
        """docstring for Meta"""
        model = User
        fields = (
            'username', 'last_name', 'first_name', 'email', 'is_superuser', 'is_staff', 'is_active', 'groups')

        widgets = {
            'groups': forms.SelectMultiple(attrs={'multiple': 'true', 'class': 'form-control w-100'})
        }