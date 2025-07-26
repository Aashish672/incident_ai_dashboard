from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
class LogUploadForm(forms.Form):
    file = forms.FileField(label="Upload CSV File")

class CustomUserCreationForm(UserCreationForm):
    email=forms.EmailField(required=True)

    class meta:
        model=User
        field=("username","email","password1","password2")

    def save(self,commit=True):
        user=super().save(commit=False)
        user.email=self.cleaned_data["email"]
        if commit:
            user.save()
        return user