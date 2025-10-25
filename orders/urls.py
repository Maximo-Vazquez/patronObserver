"""Rutas de la aplicación de pedidos."""

from django.urls import path

from .views import (
    AvanceEstadoPedidoVista,
    ControlPedidoVista,
    DatosEstadoPedidoVista,
    DefinirEstadoPedidoVista,
    PanelPedidoVista,
)

urlpatterns = [
    path("", PanelPedidoVista.as_view(), name="order-status"),
    path(
        "control/",
        ControlPedidoVista.as_view(),
        name="order-control",
    ),
    path(
        "datos/",
        DatosEstadoPedidoVista.as_view(),
        name="order-status-data",
    ),
    path(
        "definir/",
        DefinirEstadoPedidoVista.as_view(),
        name="order-status-set",
    ),
    path(
        "actualizar/",
        AvanceEstadoPedidoVista.as_view(),
        name="order-status-update",
    ),
]
