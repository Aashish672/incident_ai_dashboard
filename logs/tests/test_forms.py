"""Tests for Django forms — CustomUserCreationForm and UserUpdateForm."""

from django.contrib.auth.models import User
from django.test import TestCase

from logs.forms import CustomUserCreationForm, UserUpdateForm


class CustomUserCreationFormTest(TestCase):
    """Test the custom registration form."""

    def setUp(self):
        self.admin = User.objects.create_user("adminuser", "admin@example.com", "pass123")
        self.admin.profile.role = "admin"
        self.admin.profile.save()

    def test_valid_admin_registration(self):
        form_data = {
            "username": "newadmin",
            "email": "newadmin@example.com",
            "password1": "complexpass123!",
            "password2": "complexpass123!",
            "role": "admin",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_viewer_registration(self):
        form_data = {
            "username": "newviewer",
            "email": "viewer@example.com",
            "password1": "complexpass123!",
            "password2": "complexpass123!",
            "role": "viewer",
            "admin": self.admin.pk,
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_viewer_without_admin_fails(self):
        form_data = {
            "username": "noviewer",
            "email": "noviewer@example.com",
            "password1": "complexpass123!",
            "password2": "complexpass123!",
            "role": "viewer",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_admin_with_admin_fails(self):
        form_data = {
            "username": "badadmin",
            "email": "badadmin@example.com",
            "password1": "complexpass123!",
            "password2": "complexpass123!",
            "role": "admin",
            "admin": self.admin.pk,
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_duplicate_email_fails(self):
        form_data = {
            "username": "duplicate",
            "email": "admin@example.com",  # already exists
            "password1": "complexpass123!",
            "password2": "complexpass123!",
            "role": "admin",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_saves_profile(self):
        form_data = {
            "username": "profiletest",
            "email": "profile@example.com",
            "password1": "complexpass123!",
            "password2": "complexpass123!",
            "role": "admin",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.profile.role, "admin")


class UserUpdateFormTest(TestCase):
    """Test the profile update form."""

    def setUp(self):
        self.user = User.objects.create_user("edituser", "edit@example.com", "pass123")

    def test_valid_update(self):
        form = UserUpdateForm(
            data={
                "username": "edituser",
                "email": "newedit@example.com",
                "first_name": "Test",
                "last_name": "User",
            },
            instance=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_duplicate_email_other_user(self):
        User.objects.create_user("other", "other@example.com", "pass123")
        form = UserUpdateForm(
            data={
                "username": "edituser",
                "email": "other@example.com",
                "first_name": "Test",
                "last_name": "User",
            },
            instance=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
