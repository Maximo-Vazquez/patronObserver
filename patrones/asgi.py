"""Configuración ASGI del proyecto con soporte para Django Channels."""

from __future__ import annotations

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "patrones.settings")

aplicacion_django = get_asgi_application()

from .routing import websocket_urlpatterns  # noqa: E402

aplicacion = ProtocolTypeRouter(
    {
        "http": aplicacion_django,
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    }
)

application = aplicacion
