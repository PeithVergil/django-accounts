from django import forms
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordResetForm, ReadOnlyPasswordHashField
)

from accounts.models import User, Activation

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'span12', 'placeholder': _('Password')
    }), label=_('Password'))

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'span12', 'placeholder': _('Confirm Password')
    }), label=_('Confirm Password'))

    class Meta:
        model = User

        fields = (
            'email', 'firstname', 'lastname', 'password',
        )

        widgets = {
            'firstname': forms.TextInput(attrs={
                'class': 'span12', 'placeholder': _('First Name')
            }),
            'lastname': forms.TextInput(attrs={
                'class': 'span12', 'placeholder': _('Last Name')
            }),
            'email': forms.TextInput(attrs={
                'class': 'span12', 'placeholder': _('Email Address')
            }),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_('The two password fields did not match.'))
        return p2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class EditUserForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User

    def clean_password(self):
        return self.initial["password"]

class CustomAuthForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _('Incorrect %(username)s or password. Please try again.'),
        'no_cookies': _("Your Web browser doesn't appear to have cookies "
                        "enabled. Cookies are required for logging in."),
        'inactive': _('Your account is still inactive.'),
    }

    username = forms.EmailField(widget=forms.TextInput(attrs={
        'placeholder': _('Email Address'), 'class': 'span12'
    }), label=_('Email Address'))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': _('Password'), 'class': 'span12'
    }), label=_('Password'))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'] % {
                        'username': self.username_field.verbose_name
                    })
        self.check_for_test_cookie()
        return self.cleaned_data

class CustomPasswordResetForm(PasswordResetForm):
    error_messages = {
        'unknown': _("That email address doesn't have an associated "
                     "user account. Are you sure you've registered?"),
        'unusable': _("The user account associated with this email "
                      "address cannot reset the password."),
    }

    email = forms.EmailField(widget=forms.TextInput(attrs={
        'placeholder': _('Email Address'), 'class': 'span12'
    }), label=_('Email Address'), max_length=254)

class ActivationForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': _('Activation code'), 'class': 'span12'
    }), max_length=64)