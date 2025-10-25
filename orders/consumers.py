"""Consumidor WebSocket para transmitir el estado del pedido en tiempo real."""

from __future__ import annotations

from typing import Any, Dict

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import Order
from .servicios import construir_evento_seguimiento


class ConsumidorSeguimientoPedido(AsyncJsonWebsocketConsumer):
    """Canal WebSocket que entrega actualizaciones del pedido."""

    pedido_id: int
    grupo_pedido: str

    async def connect(self) -> None:
        """Suscribe el socket al grupo correspondiente al pedido."""

        self.pedido_id = int(self.scope["url_route"]["kwargs"]["pedido_id"])
        self.grupo_pedido = f"pedido_{self.pedido_id}"
        await self.channel_layer.group_add(self.grupo_pedido, self.channel_name)
        await self.accept()
        await self._enviar_estado_actual()

    async def disconnect(self, close_code: int) -> None:  # noqa: D401
        """Cancela la suscripción al grupo del pedido al desconectarse."""

        await self.channel_layer.group_discard(self.grupo_pedido, self.channel_name)

    async def recibir_comando(self, contenido: Dict[str, Any]) -> None:
        """Método de compatibilidad en caso de comandos futuros."""

        # Se deja como placeholder para ampliar la funcionalidad.
        return None

    async def enviar_actualizacion(self, evento: Dict[str, Any]) -> None:
        """Recibe el evento del canal y lo reenvía a la clienta."""

        await self.send_json(evento["contenido"])

    async def _enviar_estado_actual(self) -> None:
        """Obtiene el estado actual desde la base de datos y lo envía."""

        pedido = await database_sync_to_async(Order.objects.get)(pk=self.pedido_id)
        datos = construir_evento_seguimiento(pedido)
        await self.send_json(datos)
