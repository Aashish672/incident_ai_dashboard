"""Dashboard view — main analytics dashboard with charts and filters."""

import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db.models.functions import ExtractHour, TruncDate
from django.shortcuts import render

from ..models import LogEntry

logger = logging.getLogger(__name__)


@login_required
def dashboard_view(request):
    """Render the analytics dashboard with summary cards, charts, and recent logs."""
    user = request.user
    profile = user.profile

    # Role-based filtering
    if profile.role == "admin":
        viewer_users = User.objects.filter(profile__admin=user)
        logs = LogEntry.objects.filter(Q(user=user) | Q(user__in=viewer_users))
    else:
        logs = LogEntry.objects.filter(user=user)

    # Date filters from query parameters
    start = request.GET.get("start")
    end = request.GET.get("end")
    show_anomalies = request.GET.get("anomaly") == "true"

    if start:
        logs = logs.filter(timestamp__date__gte=start)
    if end:
        logs = logs.filter(timestamp__date__lte=end)
    if show_anomalies:
        logs = logs.filter(is_anomaly=True)

    total_logs = logs.count()
    total_anomalies = logs.filter(is_anomaly=True).count()

    # Level distribution
    level_counts_qs = logs.values("level").annotate(count=Count("level"))
    level_counts = {row["level"]: row["count"] for row in level_counts_qs}
    level_labels = list(level_counts.keys())
    level_values = list(level_counts.values())

    # Daily trend
    daily_logs = (
        logs.annotate(date=TruncDate("timestamp"))
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )
    date_labels = [entry["date"].strftime("%Y-%m-%d") for entry in daily_logs]
    date_data = [entry["count"] for entry in daily_logs]

    # Anomaly by hour (heatmap)
    hourly_logs = (
        logs.filter(is_anomaly=True)
        .annotate(hour=ExtractHour("timestamp"))
        .values("hour")
        .annotate(count=Count("id"))
        .order_by("hour")
    )
    hour_labels = list(range(24))
    hour_data = [0] * 24
    for row in hourly_logs:
        hour_data[row["hour"]] = row["count"]

    recent_logs = logs.order_by("-timestamp")[:10]

    context = {
        "total_logs": total_logs,
        "total_anomalies": total_anomalies,
        "level_counts": level_counts,
        "level_labels": level_labels,
        "level_data": level_values,
        "date_labels": date_labels,
        "date_data": date_data,
        "hour_labels": hour_labels,
        "hour_data": hour_data,
        "start": start,
        "end": end,
        "show_anomalies": show_anomalies,
        "recent_logs": recent_logs,
    }

    return render(request, "dashboard.html", context)
