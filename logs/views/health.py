"""Health check view — used by load balancers and monitoring."""

from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """Return health status of app and database connectivity."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({
            "status": "healthy",
            "database": "connected",
        })
    except Exception as e:
        return JsonResponse(
            {"status": "unhealthy", "error": str(e)},
            status=500,
        )
