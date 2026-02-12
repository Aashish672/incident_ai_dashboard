"""Notification views — notification list and bulk actions."""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET", "POST"])
def notification_list(request):
    """List unread notifications, with POST to mark all as read."""
    notifications = request.user.notifications.filter(is_read=False).order_by("-created_at")

    if request.method == "POST":
        notifications.update(is_read=True)

    return render(request, "notifications.html", {"notifications": notifications})


@login_required
@require_POST
def mark_all_read(request):
    """Mark all user notifications as read."""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect("logs:notifications")
