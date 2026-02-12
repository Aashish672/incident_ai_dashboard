"""DRF API views for the Incident AI Dashboard."""

import logging

from django.contrib.auth.models import User
from django.db.models import Count, Q
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import LogEntry, Notification
from .serializers import (
    DashboardStatsSerializer,
    LogEntryCreateSerializer,
    LogEntrySerializer,
    NotificationSerializer,
)

logger = logging.getLogger(__name__)


class LogEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for log entries.

    list:      GET  /api/logs/
    create:    POST /api/logs/
    retrieve:  GET  /api/logs/{id}/
    stats:     GET  /api/logs/stats/
    anomalies: GET  /api/logs/anomalies/
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["message", "source", "level"]
    ordering_fields = ["timestamp", "level", "is_anomaly"]
    ordering = ["-timestamp"]

    def get_serializer_class(self):
        if self.action == "create":
            return LogEntryCreateSerializer
        return LogEntrySerializer

    def get_queryset(self):
        user = self.request.user
        profile = user.profile

        if profile.role == "admin":
            viewer_users = User.objects.filter(profile__admin=user)
            return LogEntry.objects.filter(Q(user=user) | Q(user__in=viewer_users))
        return LogEntry.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Return summary statistics for the user's logs."""
        qs = self.get_queryset()
        total = qs.count()
        anomalies = qs.filter(is_anomaly=True).count()
        level_dist = dict(qs.values_list("level").annotate(count=Count("id")))

        data = {
            "total_logs": total,
            "total_anomalies": anomalies,
            "anomaly_rate": round(anomalies / total * 100, 2) if total > 0 else 0.0,
            "level_distribution": level_dist,
        }
        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def anomalies(self, request):
        """Return only anomaly log entries."""
        qs = self.get_queryset().filter(is_anomaly=True)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = LogEntrySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = LogEntrySerializer(qs, many=True)
        return Response(serializer.data)


class NotificationViewSet(viewsets.ModelViewSet):
    """API endpoint for user notifications."""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        count = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({"marked_read": count})
