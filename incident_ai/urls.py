"""
URL configuration for incident_ai project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.urls import reverse_lazy

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from logs import views as log_views

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Health check (for ALB/ECS health probes)
    path("health/", log_views.health_check, name="health_check"),

    # Landing page
    path("", log_views.landing_page, name="landing"),

    # ── Auth ────────────────────────────────────────────────────────────
    path("login/", auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="landing"), name="logout"),
    path("register/", log_views.register, name="register"),

    # Password reset flow
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="auth/password_reset.html",
            email_template_name="auth/password_reset_email.txt",
            subject_template_name="auth/password_reset_subject.txt",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="auth/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="auth/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="auth/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

    # Password change (logged-in users)
    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="auth/password_change.html",
            success_url=reverse_lazy("password_change_done"),
        ),
        name="password_change",
    ),
    path(
        "password-change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="auth/password_change_done.html"
        ),
        name="password_change_done",
    ),

    # Profile
    path("profile/", log_views.profile_view, name="profile"),
    path("profile/edit/", log_views.profile_edit, name="profile_edit"),

    # App urls
    path("logs/", include("logs.urls")),

    # ── REST API ────────────────────────────────────────────────────────
    path("api/", include("logs.api_urls")),

    # API documentation (Swagger / OpenAPI)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
