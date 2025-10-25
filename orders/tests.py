"""Pruebas automáticas para el patrón observador."""

from django.test import TestCase

from .models import Order
from .observer import CustomerObserver, OrderSubject


class ObserverPatternTests(TestCase):
    """Verifica que las notificaciones se generen correctamente."""

    def test_customer_receives_notification_when_status_changes(self) -> None:
        """El observador debe recibir un mensaje con el nuevo estado del pedido."""

        order = Order.objects.create(customer_name="Laura")
        subject = OrderSubject(order)
        observer = CustomerObserver(name=order.customer_name)
        subject.attach(observer)

        subject.update_status(Order.Status.SHIPPED)

        self.assertEqual(len(observer.notifications), 1)
        self.assertIn("En camino", observer.notifications[0])

    def test_next_status_includes_outside_step(self) -> None:
        """La transición automática debe incluir el estado intermedio 'outside'."""

        order = Order.objects.create(customer_name="Laura", status=Order.Status.SHIPPED)

        self.assertEqual(order.next_status(), Order.Status.OUTSIDE)
