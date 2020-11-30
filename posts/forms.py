from django import forms
from .models import User, Post

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


class PostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.filecount = kwargs.pop('filecount')
        super(PostForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = ('title', 'description', 'code_link')

    def clean(self):
        cleaned_data = super().clean()
        if self.filecount < 1:  # use your throttling utility here
            raise forms.ValidationError("You should upload atleast one image or video ")
        elif self.filecount > 3:
            raise forms.ValidationError("Cannot upload more than 3 image/video")

        return cleaned_data
