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

    def obtener_siguiente_estado(self) -> str:
        """Obtiene el siguiente estado disponible para el pedido."""

        orden_estados = list(self.Status.values)
        try:
            indice_actual = orden_estados.index(self.status)
        except ValueError:
            return self.Status.PREPARING

        if indice_actual < len(orden_estados) - 1:
            return orden_estados[indice_actual + 1]
        return self.status

    def siguiente_estado(self) -> str:
        """Alias en español para compatibilidad semántica."""

        return self.obtener_siguiente_estado()

    def next_status(self) -> str:
        """Método de compatibilidad con el nombre anterior en inglés."""

        return self.obtener_siguiente_estado()

    def esta_completado(self) -> bool:
        """Indica si el pedido ya llegó a su estado final."""

        return self.status == self.Status.DELIVERED

    def is_completed(self) -> bool:
        """Método de compatibilidad con el nombre anterior en inglés."""

        return self.esta_completado()
