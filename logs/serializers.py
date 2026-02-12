"""DRF serializers for the Incident AI Dashboard API."""

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import LogEntry, Notification, Profile


class LogEntrySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = LogEntry
        fields = [
            "id",
            "username",
            "timestamp",
            "level",
            "message",
            "source",
            "is_anomaly",
            "alert_sent",
        ]
        read_only_fields = ["id", "is_anomaly", "alert_sent"]


class LogEntryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating log entries via the API."""

    class Meta:
        model = LogEntry
        fields = ["timestamp", "level", "message", "source"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "message", "created_at", "is_read"]
        read_only_fields = ["id", "created_at"]


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ["username", "email", "role", "admin"]
        read_only_fields = ["admin"]


class DashboardStatsSerializer(serializers.Serializer):
    """Read-only serializer for dashboard summary stats."""

    total_logs = serializers.IntegerField()
    total_anomalies = serializers.IntegerField()
    anomaly_rate = serializers.FloatField()
    level_distribution = serializers.DictField(child=serializers.IntegerField())
