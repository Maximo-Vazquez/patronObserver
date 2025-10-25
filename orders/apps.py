from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Configura la aplicación de pedidos."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"
    verbose_name = "Gestor de pedidos con observador"
