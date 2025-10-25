"""Configuración del panel de administración para la app de pedidos."""

from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Muestra un listado claro de los pedidos en el admin."""

    list_display = ("customer_name", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("customer_name",)
