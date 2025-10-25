"""Rutas de la aplicación de pedidos."""

from django.urls import path

from .views import (
    OrderControlView,
    OrderDashboardView,
    OrderStatusDataView,
    OrderStatusSetView,
    OrderStatusUpdateView,
)

urlpatterns = [
    path("", OrderDashboardView.as_view(), name="order-status"),
    path(
        "control/",
        OrderControlView.as_view(),
        name="order-control",
    ),
    path(
        "datos/",
        OrderStatusDataView.as_view(),
        name="order-status-data",
    ),
    path(
        "definir/",
        OrderStatusSetView.as_view(),
        name="order-status-set",
    ),
    path("actualizar/", OrderStatusUpdateView.as_view(), name="order-status-update"),
]
