"""Rutas de WebSocket a nivel de proyecto."""

from __future__ import annotations

from orders.routing import websocket_urlpatterns as rutas_pedidos

websocket_urlpatterns = [
    *rutas_pedidos,
]
