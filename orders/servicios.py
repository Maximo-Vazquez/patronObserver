"""Funciones auxiliares en español para la aplicación de pedidos."""

from __future__ import annotations

from typing import Any, Dict, List

from .models import Order


def construir_evento_seguimiento(pedido: Order) -> Dict[str, Any]:
    """Arma la carga útil con la información del seguimiento del pedido."""

    etiquetas = dict(Order.Status.choices)
    estados = list(Order.Status.values)
    try:
        indice_actual = estados.index(pedido.status)
    except ValueError:
        indice_actual = 0

    pasos: List[Dict[str, Any]] = []
    for indice, estado in enumerate(estados):
        pasos.append(
            {
                "valor": estado,
                "etiqueta": etiquetas[estado],
                "alcanzado": indice <= indice_actual,
            }
        )

    return {
        "tipo": "seguimiento",
        "estado": pedido.status,
        "descripcion_estado": etiquetas.get(pedido.status, pedido.status),
        "actualizado": pedido.updated_at.isoformat(),
        "progreso": {"pasos": pasos},
    }
