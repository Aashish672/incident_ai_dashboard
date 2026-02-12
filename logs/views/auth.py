"""Auth views — registration and landing page."""

import logging

from django.contrib.auth import login
from django.shortcuts import redirect, render

from ..forms import CustomUserCreationForm

logger = logging.getLogger(__name__)


def register(request):
    """Handle user registration with role selection."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info("New user registered: %s", form.cleaned_data.get("username"))
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "auth/register.html", {"form": form})


def landing_page(request):
    """Render the public landing page."""
    return render(request, "landing.html")
