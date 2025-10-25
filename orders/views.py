"""Vistas de la aplicación de pedidos con nombres en español."""

from __future__ import annotations

import json

from typing import Any, Dict, List

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View

from .models import Order
from .observador import ObservadoraCliente, SujetoPedido
from .servicios import construir_evento_seguimiento


def _obtener_pedido_demo() -> Order:
    """Obtiene o crea el pedido de demostración."""

    pedido, _ = Order.objects.get_or_create(
        customer_name="Laura",
        defaults={"status": Order.Status.PREPARING},
    )
    return pedido


class PanelPedidoVista(TemplateView):
    """Pantalla principal con el resumen del pedido y su seguimiento."""

    template_name = "orders/order_dashboard.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        contexto = super().get_context_data(**kwargs)
        pedido = _obtener_pedido_demo()
        productos = [
            {
                "nombre": "Box de pastelería artesanal",
                "sku": "BOX-CAFE-01",
                "cantidad": 1,
                "precio": 34.90,
            },
            {
                "nombre": "Blend de café de especialidad 250g",
                "sku": "CAF-AR-250",
                "cantidad": 2,
                "precio": 12.50,
            },
            {
                "nombre": "Mermelada orgánica de frutos rojos",
                "sku": "MER-OR-125",
                "cantidad": 1,
                "precio": 6.75,
            },
        ]
        for producto in productos:
            producto["subtotal"] = producto["precio"] * producto["cantidad"]

        contexto.update(
            {
                "pedido": pedido,
                "opciones_estado": list(Order.Status.choices),
                "productos": productos,
                "total_pedido": sum(item["subtotal"] for item in productos),
                "total_articulos": sum(item["cantidad"] for item in productos),
                "moneda": "EGP",
            }
        )
        return contexto


class ControlPedidoVista(TemplateView):
    """Pantalla de control manual para cambiar el estado del pedido."""

    template_name = "orders/order_control.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        contexto = super().get_context_data(**kwargs)
        pedido = _obtener_pedido_demo()
        contexto.update(
            {
                "pedido": pedido,
                "opciones_estado": list(Order.Status.choices),
            }
        )
        return contexto


@method_decorator(csrf_exempt, name="dispatch")
class AvanceEstadoPedidoVista(View):
    """Recibe peticiones para avanzar el estado del pedido."""

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        pedido = _obtener_pedido_demo()
        if pedido.esta_completado():
            return JsonResponse(
                {
                    "estado": pedido.status,
                    "descripcion_estado": pedido.get_status_display(),
                    "notificaciones": [
                        "El pedido ya fue entregado, no hay nuevos cambios que notificar."
                    ],
                    "completado": True,
                }
            )

        sujeto = SujetoPedido(pedido)
        observadora = ObservadoraCliente(nombre=pedido.customer_name)
        sujeto.agregar_observadora(observadora)

        nuevo_estado = pedido.obtener_siguiente_estado()
        notificaciones: List[str] = sujeto.actualizar_estado(nuevo_estado)
        pedido.refresh_from_db(fields=["status", "updated_at"])

        return JsonResponse(
            {
                "estado": pedido.status,
                "descripcion_estado": pedido.get_status_display(),
                "notificaciones": notificaciones,
                "completado": pedido.esta_completado(),
            }
        )


class DatosEstadoPedidoVista(View):
    """Devuelve el estado actual del pedido para la pantalla informativa."""

    http_method_names = ["get"]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        pedido = _obtener_pedido_demo()
        datos = construir_evento_seguimiento(pedido)
        return JsonResponse(datos)


@method_decorator(csrf_exempt, name="dispatch")
class DefinirEstadoPedidoVista(View):
    """Permite establecer manualmente el estado del pedido desde la consola."""

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        pedido = _obtener_pedido_demo()
        try:
            datos = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            datos = {}
        nuevo_estado = datos.get("estado")

        if nuevo_estado not in dict(Order.Status.choices):
            return JsonResponse(
                {
                    "error": "El estado recibido no es válido.",
                },
                status=400,
            )

        sujeto = SujetoPedido(pedido)
        observadora = ObservadoraCliente(nombre=pedido.customer_name)
        sujeto.agregar_observadora(observadora)

        notificaciones: List[str] = sujeto.actualizar_estado(nuevo_estado)
        pedido.refresh_from_db(fields=["status", "updated_at"])

        respuesta = construir_evento_seguimiento(pedido)
        respuesta.update(
            {
                "notificaciones": notificaciones,
            }
        )
        return JsonResponse(respuesta)
