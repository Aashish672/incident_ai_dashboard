"""Profile views — user profile display and edit."""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import UserUpdateForm
from ..models import LogEntry

logger = logging.getLogger(__name__)


@login_required
def profile_view(request):
    """Display user profile with stats and role info."""
    profile = getattr(request.user, "profile", None)

    logs_count = LogEntry.objects.filter(user=request.user).count()
    anomalies_count = LogEntry.objects.filter(user=request.user, is_anomaly=True).count()
    recent_logs = LogEntry.objects.filter(user=request.user).order_by("-timestamp")[:5]

    admin = None
    assigned_viewers = []

    if profile:
        if profile.role == "viewer":
            admin = profile.admin
        elif profile.role == "admin":
            assigned_viewers = request.user.viewers.all()

    context = {
        "user": request.user,
        "profile": profile,
        "logs_count": logs_count,
        "anomalies_count": anomalies_count,
        "recent_logs": recent_logs,
        "admin": admin,
        "assigned_viewers": assigned_viewers,
    }
    return render(request, "auth/profile.html", context)


@login_required
def profile_edit(request):
    """Handle profile information editing."""
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("profile")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, "auth/profile_edit.html", {"form": form})
