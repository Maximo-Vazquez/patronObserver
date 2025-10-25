"""Implementación del patrón observador usando canales de Django."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Protocol

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Order
from .servicios import construir_evento_seguimiento


class ObservadoraPedido(Protocol):
    """Define la interfaz mínima que deben seguir las observadoras."""

    def actualizar(self, pedido: Order) -> str:
        """Recibe el pedido y devuelve un mensaje de notificación."""

    def update(self, pedido: Order) -> str:  # pragma: no cover - compatibilidad
        """Alias en inglés para mantener compatibilidad retroactiva."""


@dataclass
class ObservadoraCliente:
    """Observadora concreta que representa a la clienta que espera el pedido."""

    nombre: str
    notificaciones: List[str] = field(default_factory=list)

    def actualizar(self, pedido: Order) -> str:
        """Genera un mensaje de actualización para el pedido observado."""

        etiqueta_estado = pedido.get_status_display()
        mensaje = (
            f"{self.nombre} recibe una notificación: tu pedido ahora está '{etiqueta_estado}'."
        )
        self.notificaciones.append(mensaje)
        return mensaje

    def update(self, pedido: Order) -> str:  # pragma: no cover - compatibilidad
        """Alias en inglés para integraciones existentes."""

        return self.actualizar(pedido)


class SujetoPedido:
    """Gestiona la lista de observadoras y emite notificaciones."""

    def __init__(self, pedido: Order) -> None:
        self.pedido = pedido
        self._observadoras: List[ObservadoraPedido] = []

    def agregar_observadora(self, observadora: ObservadoraPedido) -> None:
        """Agrega una nueva observadora a la lista de suscriptoras."""

        if observadora not in self._observadoras:
            self._observadoras.append(observadora)

    def remover_observadora(self, observadora: ObservadoraPedido) -> None:
        """Elimina una observadora de la lista de suscriptoras."""

        if observadora in self._observadoras:
            self._observadoras.remove(observadora)

    def notificar(self) -> Iterable[str]:
        """Notifica a todas las suscriptoras y devuelve los mensajes emitidos."""

        for observadora in list(self._observadoras):
            if hasattr(observadora, "actualizar"):
                yield observadora.actualizar(self.pedido)
            else:  # pragma: no cover - ruta de compatibilidad
                yield observadora.update(self.pedido)

    def actualizar_estado(self, nuevo_estado: str) -> List[str]:
        """Actualiza el estado del pedido y notifica a las observadoras."""

        self.pedido.status = nuevo_estado
        self.pedido.save(update_fields=["status", "updated_at"])
        self._difundir_actualizacion_en_tiempo_real()
        return list(self.notificar())

    def _difundir_actualizacion_en_tiempo_real(self) -> None:
        """Envía el estado actual por WebSocket mediante Django Channels."""

        capa = get_channel_layer()
        if capa is None:
            return

        datos_seguimiento = construir_evento_seguimiento(self.pedido)
        grupo = f"pedido_{self.pedido.pk}"
        async_to_sync(capa.group_send)(
            grupo,
            {
                "type": "enviar_actualizacion",
                "contenido": datos_seguimiento,
            },
        )

    # Alias de compatibilidad con la versión previa en inglés
    attach = agregar_observadora
    detach = remover_observadora
    notify = notificar
    update_status = actualizar_estado
