"""Export views — CSV and PDF exports for logs and anomalies."""

import base64
import csv
import io
import logging

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.timezone import now
from weasyprint import HTML

from ..models import LogEntry

logger = logging.getLogger(__name__)


@login_required
def export_logs_csv(request):
    """Export filtered logs as a CSV file."""
    user = request.user
    profile = user.profile

    if profile.role == "admin":
        viewer_users = user.viewers.all()
        logs = LogEntry.objects.filter(Q(user=user) | Q(user__in=viewer_users))
    else:
        logs = LogEntry.objects.filter(user=user)

    logs = logs.order_by("-timestamp")

    # Apply filters
    level = request.GET.get("level")
    show_anomalies = request.GET.get("anomaly") == "true"
    start_date = request.GET.get("start")
    end_date = request.GET.get("end")

    if level:
        logs = logs.filter(level=level)
    if show_anomalies:
        logs = logs.filter(is_anomaly=True)
    if start_date and end_date:
        logs = logs.filter(timestamp__range=[start_date, end_date])

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="filtered_logs.csv"'

    writer = csv.writer(response)
    writer.writerow(["Timestamp", "Level", "Message", "Source", "Anomaly"])

    for log in logs:
        writer.writerow([log.timestamp, log.level, log.message, log.source, log.is_anomaly])

    logger.info("User %s exported %d logs as CSV.", user.username, logs.count())
    return response


@login_required
def export_anomalies_csv(request):
    """Export anomaly-only logs as a CSV file."""
    user = request.user
    profile = user.profile

    if profile.role == "admin":
        viewer_users = user.viewers.all()
        anomalies = LogEntry.objects.filter(
            Q(user=user) | Q(user__in=viewer_users),
            is_anomaly=True,
        ).order_by("-timestamp")
    else:
        anomalies = LogEntry.objects.filter(user=user, is_anomaly=True).order_by("-timestamp")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="anomalies.csv"'

    writer = csv.writer(response)
    writer.writerow(["Timestamp", "Level", "Message", "Source"])

    for log in anomalies:
        writer.writerow([log.timestamp, log.level, log.message, log.source])

    logger.info("User %s exported anomalies CSV.", user.username)
    return response


@login_required
def export_dashboard_pdf(request):
    """Generate a PDF report of the dashboard with stats and charts."""
    user = request.user
    profile = user.profile

    if profile.role == "admin":
        viewer_users = user.viewers.all()
        log_qs = LogEntry.objects.filter(Q(user=user) | Q(user__in=viewer_users)).order_by(
            "-timestamp"
        )
    else:
        log_qs = LogEntry.objects.filter(user=user).order_by("-timestamp")

    total_logs = log_qs.count()
    total_anomalies = log_qs.filter(is_anomaly=True).count()
    level_counts_qs = log_qs.values("level").annotate(count=Count("level"))
    level_counts = {row["level"]: row["count"] for row in level_counts_qs}

    logs = log_qs[:20]

    # Create chart
    plt.figure(figsize=(6, 3))
    if level_counts:
        plt.bar(level_counts.keys(), level_counts.values(), color="skyblue")
    plt.title("Log Levels Distribution")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    chart_image = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()

    html_content = render_to_string(
        "export_pdf.html",
        {
            "total_logs": total_logs,
            "total_anomalies": total_anomalies,
            "level_counts": level_counts,
            "logs": logs,
            "report_date": now().strftime("%Y-%m-%d %H:%M"),
            "chart_image": f"data:image/png;base64,{chart_image}",
        },
    )

    pdf_file = HTML(string=html_content).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="incident_report.pdf"'
    logger.info("User %s generated PDF report.", user.username)
    return response
