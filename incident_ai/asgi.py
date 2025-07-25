"""
ASGI config for incident_ai project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import logs.routing  # make sure this file defines websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'incident_ai.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(        # Wrap WebSocket routes with auth support
        URLRouter(
            logs.routing.websocket_urlpatterns
        )
    ),
})
