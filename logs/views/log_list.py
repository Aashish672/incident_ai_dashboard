"""Log list views — log listing, filtering, pagination, and detail."""

import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from ..models import LogEntry

logger = logging.getLogger(__name__)


@login_required
def log_list(request):
    """List logs with filtering, search, and pagination."""
    user = request.user
    profile = user.profile

    if profile.role == "admin":
        viewer_users = User.objects.filter(profile__admin=user)
        users_qs = Q(user=user) | Q(user__in=viewer_users)
        logs = LogEntry.objects.filter(users_qs)
    else:
        logs = LogEntry.objects.filter(user=user)

    logs = logs.order_by("-timestamp")

    # Apply filters
    level = request.GET.get("level")
    search_query = request.GET.get("search", "").strip()
    show_anomalies = request.GET.get("anomaly") == "true"

    if show_anomalies:
        logs = logs.filter(is_anomaly=True)
    if level:
        logs = logs.filter(level=level)
    if search_query:
        logs = logs.filter(Q(message__icontains=search_query) | Q(source__icontains=search_query))

    paginator = Paginator(logs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "level": level,
        "search": search_query,
        "show_anomalies": show_anomalies,
    }

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "_log_list_partial.html", context)

    return render(request, "log_list.html", context)


def log_detail(request, pk):
    """Display a single log entry's full details."""
    log = get_object_or_404(LogEntry, pk=pk)
    return render(request, "log_detail.html", {"log": log})


@login_required
def user_hierarchy(request):
    """Show admin/viewer hierarchy tree."""
    admins = User.objects.filter(profile__role="admin").prefetch_related("viewers")
    viewers = User.objects.filter(profile__role="viewer").select_related("profile__admin")

    context = {"admins": admins, "viewers": viewers}
    return render(request, "user_hierarchy.html", context)
