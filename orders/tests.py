"""Pruebas automáticas para el patrón observador con canales."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.test import TestCase

from .models import Order
from .observador import ObservadoraCliente, SujetoPedido
from .servicios import construir_evento_seguimiento


class PruebasPatronObservador(TestCase):
    """Verifica que las notificaciones se generen correctamente."""

    def test_clienta_recibe_notificacion_al_cambiar_estado(self) -> None:
        """La observadora debe recibir un mensaje con el nuevo estado del pedido."""

        pedido = Order.objects.create(customer_name="Laura")
        sujeto = SujetoPedido(pedido)
        observadora = ObservadoraCliente(nombre=pedido.customer_name)
        sujeto.agregar_observadora(observadora)

        sujeto.actualizar_estado(Order.Status.SHIPPED)

        self.assertEqual(len(observadora.notificaciones), 1)
        self.assertIn("En camino", observadora.notificaciones[0])

    def test_siguiente_estado_incluye_paso_externo(self) -> None:
        """La transición automática debe incluir el estado intermedio 'outside'."""

        pedido = Order.objects.create(customer_name="Laura", status=Order.Status.SHIPPED)

        self.assertEqual(pedido.obtener_siguiente_estado(), Order.Status.OUTSIDE)

    def test_evento_de_seguimiento_contiene_progreso(self) -> None:
        """El servicio debe construir un payload con pasos alcanzados."""

        pedido = Order.objects.create(customer_name="Laura", status=Order.Status.OUTSIDE)
        evento = construir_evento_seguimiento(pedido)

        self.assertEqual(evento["estado"], Order.Status.OUTSIDE)
        self.assertTrue(evento["progreso"]["pasos"][2]["alcanzado"])

    def test_canal_recibe_actualizacion_en_tiempo_real(self) -> None:
        """El sujeto debe enviar la actualización mediante Django Channels."""

        capa = get_channel_layer()
        self.assertIsNotNone(capa)
        if capa is None:  # Protección adicional para mypy
            self.fail("No se obtuvo una capa de canales para las pruebas.")

        pedido = Order.objects.create(customer_name="Laura")
        sujeto = SujetoPedido(pedido)

        nombre_canal = async_to_sync(capa.new_channel)("test_")
        grupo = f"pedido_{pedido.pk}"
        async_to_sync(capa.group_add)(grupo, nombre_canal)

        sujeto.actualizar_estado(Order.Status.SHIPPED)

        mensaje = async_to_sync(capa.receive)(nombre_canal)
        self.assertEqual(mensaje["type"], "enviar_actualizacion")
        self.assertEqual(mensaje["contenido"]["estado"], Order.Status.SHIPPED)
