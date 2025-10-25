"""Vistas que exponen el patrón observador mediante la web."""

from __future__ import annotations

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


class OrderStatusView(TemplateView):
    """Página principal que muestra el estado del pedido y las notificaciones."""

    template_name = "orders/order_status.html"

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
