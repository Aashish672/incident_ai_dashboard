"""Tests for views — access control, response codes, and redirects."""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from logs.models import LogEntry


class AuthViewTest(TestCase):
    """Test authentication-related views."""

    def test_landing_page_accessible(self):
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)

    def test_register_page_accessible(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_login_page_accessible(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)


class DashboardAccessTest(TestCase):
    """Test dashboard access control."""

    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "testpass123")
        self.user.profile.role = "admin"
        self.user.profile.save()

    def test_unauthenticated_redirect(self):
        response = self.client.get(reverse("logs:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_authenticated_access(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("logs:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_context_data(self):
        self.client.login(username="testuser", password="testpass123")
        LogEntry.objects.create(
            user=self.user,
            timestamp=timezone.now(),
            level="ERROR",
            message="Test error",
            is_anomaly=True,
        )
        response = self.client.get(reverse("logs:dashboard"))
        self.assertIn("total_logs", response.context)
        self.assertIn("total_anomalies", response.context)
        self.assertEqual(response.context["total_logs"], 1)
        self.assertEqual(response.context["total_anomalies"], 1)


class UploadViewTest(TestCase):
    """Test log upload view."""

    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "testpass123")
        self.user.profile.role = "admin"
        self.user.profile.save()

    def test_upload_requires_login(self):
        response = self.client.get(reverse("logs:upload_logs"))
        self.assertEqual(response.status_code, 302)

    def test_upload_page_accessible(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("logs:upload_logs"))
        self.assertEqual(response.status_code, 200)


class LogListViewTest(TestCase):
    """Test log list and detail views."""

    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "testpass123")
        self.user.profile.role = "admin"
        self.user.profile.save()
        self.log = LogEntry.objects.create(
            user=self.user,
            timestamp=timezone.now(),
            level="INFO",
            message="Test log",
            source="test",
        )

    def test_log_list_requires_login(self):
        response = self.client.get(reverse("logs:log_list"))
        self.assertEqual(response.status_code, 302)

    def test_log_list_authenticated(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("logs:log_list"))
        self.assertEqual(response.status_code, 200)

    def test_log_detail(self):
        response = self.client.get(reverse("logs:log_detail", kwargs={"pk": self.log.pk}))
        self.assertEqual(response.status_code, 200)

    def test_log_list_filter_anomalies(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("logs:log_list") + "?anomaly=true")
        self.assertEqual(response.status_code, 200)


class ExportViewTest(TestCase):
    """Test CSV and PDF export views."""

    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "testpass123")
        self.user.profile.role = "admin"
        self.user.profile.save()

    def test_export_csv_requires_login(self):
        response = self.client.get(reverse("logs:export_logs_csv"))
        self.assertEqual(response.status_code, 302)

    def test_export_csv_authenticated(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("logs:export_logs_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")


class HealthCheckTest(TestCase):
    """Test health check endpoint."""

    def test_health_check_returns_json(self):
        response = self.client.get(reverse("health_check"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database"], "connected")


class NotificationViewTest(TestCase):
    """Test notification views."""

    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "testpass123")
        self.user.profile.role = "admin"
        self.user.profile.save()

    def test_notifications_requires_login(self):
        response = self.client.get(reverse("logs:notifications"))
        self.assertEqual(response.status_code, 302)

    def test_notifications_authenticated(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("logs:notifications"))
        self.assertEqual(response.status_code, 200)
