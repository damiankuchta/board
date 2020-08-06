from django.contrib.auth.forms import UserCreationForm
from django import forms

from . import models


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta():
        model = models.User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        self.instance.is_active = False
        return super().save()


