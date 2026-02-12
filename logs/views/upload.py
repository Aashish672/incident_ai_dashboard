"""Upload view — CSV log file upload and initial processing."""

import csv
import io
import logging
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import LogUploadForm
from ..models import LogEntry, Notification
from ..tasks import process_logs_sync

logger = logging.getLogger(__name__)


@login_required
def upload_logs(request):
    """Handle CSV log file upload, persist entries, and trigger async ML pipeline."""
    logs = []
    anomalies = []

    if request.method == "POST":
        form = LogUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            decoded = file.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(decoded))

            for row in reader:
                try:
                    timestamp = datetime.fromisoformat(row["timestamp"])
                except (ValueError, KeyError):
                    messages.error(
                        request, f"Invalid timestamp format: {row.get('timestamp', 'N/A')}"
                    )
                    continue

                log = LogEntry.objects.create(
                    user=request.user,
                    timestamp=timestamp,
                    level=row.get("level", "INFO"),
                    message=row.get("message", ""),
                    source=row.get("source", ""),
                )
                logs.append(log)

            # Run anomaly detection pipeline synchronously
            process_logs_sync()

            messages.success(
                request,
                f"Uploaded {len(logs)} logs. Anomaly detection completed.",
            )
            logger.info("User %s uploaded %d logs.", request.user.username, len(logs))
            return redirect("logs:dashboard")
    else:
        form = LogUploadForm()

    return render(
        request,
        "upload_logs.html",
        {"form": form, "logs": logs, "anomalies": anomalies},
    )
