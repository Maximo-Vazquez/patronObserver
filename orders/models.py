"""Modelos de la aplicación de pedidos."""

from django.db import models


class Order(models.Model):
    """Representa el pedido de una clienta que espera cambios de estado."""

    class Status(models.TextChoices):
        PREPARING = "preparing", "Preparando pedido"
        SHIPPED = "shipped", "En camino"
        OUTSIDE = "outside", "Afuera"
        DELIVERED = "delivered", "Entregado"

    customer_name = models.CharField(
        max_length=100,
        help_text="Nombre de la clienta que recibirá las notificaciones.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PREPARING,
        help_text="Estado actual del pedido mostrado en la interfaz.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Marca temporal del momento en el que se creó el pedido.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Marca temporal de la última actualización del pedido.",
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self) -> str:
        """Devuelve una representación legible del pedido."""

        return f"Pedido de {self.customer_name}"

    def next_status(self) -> str:
        """Obtiene el siguiente estado disponible para el pedido."""

        status_order = list(self.Status.values)
        try:
            current_index = status_order.index(self.status)
        except ValueError:
            return self.Status.PREPARING

        if current_index < len(status_order) - 1:
            return status_order[current_index + 1]
        return self.status

    def is_completed(self) -> bool:
        """Indica si el pedido ya llegó a su estado final."""

        return self.status == self.Status.DELIVERED
