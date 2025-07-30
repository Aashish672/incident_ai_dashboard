from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import LogEntry,Profile

class LogUploadForm(forms.Form):
    file = forms.FileField(label="Upload CSV File")

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)
    admin = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role='admin'),
        required=False,
        help_text="Assign admin if registering as a viewer."
    )
    class Meta:  # Corrected from "meta"
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def clean(self):
        cleaned_data=super().clean()
        role=cleaned_data.get("role")
        admin=cleaned_data.get("admin")
        if role == 'viewer' and not admin:
            raise forms.ValidationError("Viewers must be assigned an admin.")
        if role == 'admin' and admin:
            raise forms.ValidationError("Admins cannot have an admin assigned.")
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # Only create a Profile if one does not exist
            profile,created=Profile.objects.get_or_create(
                user=user,
                defaults={
                    'role': self.cleaned_data["role"],
                    'admin': self.cleaned_data.get("admin") if self.cleaned_data["role"] == "viewer" else None,
                }
            )
            if not created:
                profile.role=self.cleaned_data["role"]
                if self.cleaned_data["role"] == "viewer":
                    profile.admin = self.cleaned_data.get("admin")
                else:
                    profile.admin = None
                profile.save()
        return user


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def clean_email(self):  # Corrected method name
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already taken.")  # Fixed typo
        return email
