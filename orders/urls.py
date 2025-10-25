"""Rutas de la aplicación de pedidos."""

from django.urls import path

from .views import OrderStatusUpdateView, OrderStatusView

urlpatterns = [
    path("", OrderStatusView.as_view(), name="order-status"),
    path("actualizar/", OrderStatusUpdateView.as_view(), name="order-status-update"),
]
