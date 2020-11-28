from django import forms
from .models import User

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        fields = ("username", "email", "password1", "password2")
        model = get_user_model()


class UserEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        fields = ("first_name", "last_name", "email", "bio",)
        model = get_user_model()
