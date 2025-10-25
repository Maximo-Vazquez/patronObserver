"""Rutas WebSocket específicas de la aplicación de pedidos."""

from __future__ import annotations

from django.urls import path

from .consumers import ConsumidorSeguimientoPedido

websocket_urlpatterns = [
    path("ws/pedidos/<int:pedido_id>/", ConsumidorSeguimientoPedido.as_asgi()),
]
