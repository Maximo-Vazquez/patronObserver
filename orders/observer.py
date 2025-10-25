"""Implementación del patrón observador para los pedidos."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Protocol

from .models import Order


class OrderObserver(Protocol):
    """Define la interfaz que deben seguir los observadores."""

    def update(self, order: Order) -> str:
        """Recibe el pedido y devuelve un mensaje de notificación."""


@dataclass
class CustomerObserver:
    """Observador concreto que representa a la clienta que espera el pedido."""

    name: str
    notifications: List[str] = field(default_factory=list)

    def update(self, order: Order) -> str:
        """Genera un mensaje de actualización para el pedido observado."""

        status_label = order.get_status_display()
        message = (
            f"{self.name} recibe una notificación: tu pedido ahora está '{status_label}'."
        )
        self.notifications.append(message)
        return message


class OrderSubject:
    """Gestiona la lista de observadores y emite notificaciones."""

    def __init__(self, order: Order) -> None:
        self.order = order
        self._observers: List[OrderObserver] = []

    def attach(self, observer: OrderObserver) -> None:
        """Agrega un nuevo observador a la lista de suscriptores."""

        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: OrderObserver) -> None:
        """Elimina un observador de la lista de suscriptores."""

        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self) -> Iterable[str]:
        """Notifica a todas las suscriptoras y devuelve los mensajes emitidos."""

        for observer in list(self._observers):
            yield observer.update(self.order)

    def update_status(self, new_status: str) -> List[str]:
        """Actualiza el estado del pedido y notifica a las observadoras."""

        self.order.status = new_status
        self.order.save(update_fields=["status", "updated_at"])
        return list(self.notify())
