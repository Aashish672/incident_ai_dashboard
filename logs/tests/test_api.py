"""Tests for the REST API endpoints."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from logs.models import LogEntry, Notification


class LogEntryAPITest(TestCase):
    """Test suite for the LogEntry API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("apiuser", "api@example.com", "pass123")
        self.user.profile.role = "admin"
        self.user.profile.save()
        self.client.force_authenticate(user=self.user)

        self.log = LogEntry.objects.create(
            user=self.user,
            timestamp=timezone.now(),
            level="ERROR",
            message="Test API log",
            source="api-test",
            is_anomaly=True,
        )

    def test_list_logs(self):
        response = self.client.get("/api/logs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_retrieve_log(self):
        response = self.client.get(f"/api/logs/{self.log.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Test API log")

    def test_create_log(self):
        data = {
            "timestamp": timezone.now().isoformat(),
            "level": "WARNING",
            "message": "New API log",
            "source": "api-test",
        }
        response = self.client.post("/api/logs/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_stats_endpoint(self):
        response = self.client.get("/api/logs/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_logs", response.data)
        self.assertIn("anomaly_rate", response.data)

    def test_anomalies_endpoint(self):
        response = self.client.get("/api/logs/anomalies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/logs/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_filter(self):
        response = self.client.get("/api/logs/?search=API")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ordering(self):
        response = self.client.get("/api/logs/?ordering=-timestamp")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NotificationAPITest(TestCase):
    """Test suite for the Notification API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("apiuser", "api@example.com", "pass123")
        self.client.force_authenticate(user=self.user)

        Notification.objects.create(user=self.user, message="Test notification 1")
        Notification.objects.create(user=self.user, message="Test notification 2")

    def test_list_notifications(self):
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_all_read(self):
        response = self.client.post("/api/notifications/mark_all_read/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["marked_read"], 2)

        # Verify all are read
        unread = Notification.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread, 0)
