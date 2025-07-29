from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import LogEntry

class LogUploadForm(forms.Form):
    file = forms.FileField(label="Upload CSV File")

class CustomUserCreationForm(UserCreationForm):
    email=forms.EmailField(required=True)

    class meta:
        model=User
        fields=("username","email","password1","password2")

    def clean_email(self):
        email=self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self,commit=True):
        user=super().save(commit=False)
        user.email=self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    

class UserUpdateForm(forms.ModelForm):
    """Allow users to edit username, email, first/last name."""
    email=forms.EmailField(required=True)

    class Meta:
        model=User
        fields=("username","email","first_name","last_name")

    def clean_mail(self):
        email=self.cleaned_data.get("email")
        qs=User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already token.")
        return email