"""REST API URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api_views

router = DefaultRouter()
router.register(r"logs", api_views.LogEntryViewSet, basename="api-logs")
router.register(r"notifications", api_views.NotificationViewSet, basename="api-notifications")

urlpatterns = [
    path("", include(router.urls)),
]
