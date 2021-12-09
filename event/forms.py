from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.utils.translation import gettext_lazy as _


# Create your forms here.

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label='Name')
    username = forms.CharField(required=True, label='User Name')

    class Meta:
        model = User
        fields = ("first_name", "username", "email", "password1", "password2")


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter a valid user name'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}), required=True)
    error_css_class = 'errorlist'

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password."
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    class Meta:
        model = User
        fields = ("username", "password")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.layout = Layout(
                Row(
                    Column('username', css_class='mb-4'),
                    Column('password', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),

            )

# def save(self, commit=True):
#     user = super(NewUserForm, self).save(commit=False)
#     user.email = self.cleaned_data['email']
#     if commit:
#         user.save()
#     return user
