"""Vistas que exponen el patrón observador mediante la web."""

from __future__ import annotations

import json

from typing import Any, Dict, List

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View

from .models import Order
from .observer import CustomerObserver, OrderSubject


def _get_demo_order() -> Order:
    """Obtiene o crea el pedido de demostración."""

    order, _ = Order.objects.get_or_create(
        customer_name="Laura",
        defaults={"status": Order.Status.PREPARING},
    )
    return order


class OrderDashboardView(TemplateView):
    """Pantalla principal con el resumen del pedido y su seguimiento."""

    template_name = "orders/order_dashboard.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        order = _get_demo_order()
        products = [
            {
                "name": "Box de pastelería artesanal",
                "sku": "BOX-CAFE-01",
                "quantity": 1,
                "price": 34.90,
            },
            {
                "name": "Blend de café de especialidad 250g",
                "sku": "CAF-AR-250",
                "quantity": 2,
                "price": 12.50,
            },
            {
                "name": "Mermelada orgánica de frutos rojos",
                "sku": "MER-OR-125",
                "quantity": 1,
                "price": 6.75,
            },
        ]
        for product in products:
            product["line_total"] = product["price"] * product["quantity"]

        context.update(
            {
                "order": order,
                "status_choices": list(Order.Status.choices),
                "products": products,
                "order_total": sum(item["line_total"] for item in products),
            }
        )
        return context


class OrderControlView(TemplateView):
    """Pantalla de control manual para cambiar el estado del pedido."""

    template_name = "orders/order_control.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        order = _get_demo_order()
        context.update(
            {
                "order": order,
                "status_choices": list(Order.Status.choices),
            }
        )
        return context


@method_decorator(csrf_exempt, name="dispatch")
class OrderStatusUpdateView(View):
    """Recibe peticiones AJAX para avanzar el estado del pedido."""

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        order = _get_demo_order()
        if order.is_completed():
            return JsonResponse(
                {
                    "status": order.status,
                    "status_display": order.get_status_display(),
                    "notifications": [
                        "El pedido ya fue entregado, no hay nuevos cambios que notificar."
                    ],
                    "completed": True,
                }
            )

        subject = OrderSubject(order)
        observer = CustomerObserver(name=order.customer_name)
        subject.attach(observer)

        new_status = order.next_status()
        notifications: List[str] = subject.update_status(new_status)
        order.refresh_from_db(fields=["status"])

        return JsonResponse(
            {
                "status": order.status,
                "status_display": order.get_status_display(),
                "notifications": notifications,
                "completed": order.is_completed(),
            }
        )


class OrderStatusDataView(View):
    """Devuelve el estado actual del pedido para la pantalla informativa."""

    http_method_names = ["get"]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        order = _get_demo_order()
        status_choices = list(Order.Status.values)
        try:
            current_index = status_choices.index(order.status)
        except ValueError:
            current_index = 0
        labels = dict(Order.Status.choices)
        return JsonResponse(
            {
                "status": order.status,
                "status_display": order.get_status_display(),
                "updated_at": order.updated_at.isoformat(),
                "progress": {
                    "steps": [
                        {
                            "value": choice,
                            "label": labels[choice],
                            "reached": index <= current_index,
                        }
                        for index, choice in enumerate(status_choices)
                    ]
                },
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class OrderStatusSetView(View):
    """Permite establecer manualmente el estado del pedido desde la consola."""

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        order = _get_demo_order()
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            data = {}
        new_status = data.get("status")

        if new_status not in dict(Order.Status.choices):
            return JsonResponse(
                {
                    "error": "El estado recibido no es válido.",
                },
                status=400,
            )

        subject = OrderSubject(order)
        observer = CustomerObserver(name=order.customer_name)
        subject.attach(observer)

        notifications: List[str] = subject.update_status(new_status)
        order.refresh_from_db(fields=["status", "updated_at"])

        return JsonResponse(
            {
                "status": order.status,
                "status_display": order.get_status_display(),
                "updated_at": order.updated_at.isoformat(),
                "notifications": notifications,
            }
        )
