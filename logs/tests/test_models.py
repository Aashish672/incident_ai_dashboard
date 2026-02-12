"""Tests for the LogEntry, Profile, and Notification models."""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from logs.models import LogEntry, Notification, Profile


class LogEntryModelTest(TestCase):
    """Test suite for the LogEntry model."""

    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "testpass123")

    def test_create_log_entry(self):
        log = LogEntry.objects.create(
            user=self.user,
            timestamp=timezone.now(),
            level="INFO",
            message="Test log message",
            source="test-server",
        )
        self.assertEqual(log.level, "INFO")
        self.assertEqual(log.user, self.user)
        self.assertFalse(log.is_anomaly)
        self.assertFalse(log.alert_sent)

    def test_anomaly_default_false(self):
        log = LogEntry.objects.create(
            user=self.user,
            timestamp=timezone.now(),
            level="ERROR",
            message="Error occurred",
        )
        self.assertFalse(log.is_anomaly)

    def test_str_representation(self):
        log = LogEntry.objects.create(
            user=self.user,
            timestamp=timezone.now(),
            level="WARNING",
            message="This is a warning message that is very long and should be truncated",
        )
        self.assertIn("WARNING", str(log))

    def test_log_ordering_by_timestamp(self):
        now = timezone.now()
        log1 = LogEntry.objects.create(
            user=self.user, timestamp=now, level="INFO", message="First"
        )
        log2 = LogEntry.objects.create(
            user=self.user,
            timestamp=now + timezone.timedelta(hours=1),
            level="ERROR",
            message="Second",
        )
        logs = LogEntry.objects.filter(user=self.user).order_by("-timestamp")
        self.assertEqual(logs.first(), log2)


class ProfileModelTest(TestCase):
    """Test suite for the Profile model."""

    def setUp(self):
        self.admin_user = User.objects.create_user("admin", "admin@example.com", "pass123")
        self.admin_user.profile.role = "admin"
        self.admin_user.profile.save()

    def test_profile_auto_created_on_user_create(self):
        user = User.objects.create_user("newuser", "new@example.com", "pass123")
        self.assertTrue(hasattr(user, "profile"))
        self.assertEqual(user.profile.role, "viewer")

    def test_admin_cannot_have_admin_assigned(self):
        self.admin_user.profile.admin = self.admin_user
        with self.assertRaises(ValidationError):
            self.admin_user.profile.clean()

    def test_viewer_must_have_admin(self):
        viewer = User.objects.create_user("viewer", "viewer@example.com", "pass123")
        viewer.profile.role = "viewer"
        viewer.profile.admin = None
        with self.assertRaises(ValidationError):
            viewer.profile.clean()

    def test_viewer_with_admin_passes_validation(self):
        viewer = User.objects.create_user("viewer", "viewer@example.com", "pass123")
        viewer.profile.role = "viewer"
        viewer.profile.admin = self.admin_user
        viewer.profile.clean()  # Should not raise

    def test_str_representation(self):
        self.assertIn("admin", str(self.admin_user.profile))


class NotificationModelTest(TestCase):
    """Test suite for the Notification model."""

    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "pass123")

    def test_create_notification(self):
        notif = Notification.objects.create(user=self.user, message="Test notification")
        self.assertFalse(notif.is_read)
        self.assertIsNotNone(notif.created_at)

    def test_str_representation(self):
        notif = Notification.objects.create(user=self.user, message="Alert triggered")
        self.assertIn("testuser", str(notif))

    def test_notification_queryset_unread(self):
        Notification.objects.create(user=self.user, message="Unread 1")
        Notification.objects.create(user=self.user, message="Unread 2")
        read = Notification.objects.create(user=self.user, message="Read")
        read.is_read = True
        read.save()

        unread = Notification.objects.filter(user=self.user, is_read=False)
        self.assertEqual(unread.count(), 2)
