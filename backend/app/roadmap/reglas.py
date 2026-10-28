"""Reglas de negocio puras para el dominio de Roadmap Personal.

Funciones puras (sin base de datos, sin HTTP) que implementan las reglas
definidas en BackendSchema.md §1.2/§3.5 y TRD.md TD-004.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from app.catalogo.reglas import EstadoCurso
from app.compartido.errores import ReglaNegocioError


class EstadoRoadmapItem(str, Enum):
    """Estados posibles para un ítem dentro del roadmap del estudiante."""
    PENDIENTE = "pendiente"
    EN_CURSO = "en_curso"
    COMPLETADO = "completado"


LIMITE_MAXIMO_ROADMAP_ITEMS = 50


def agregar_curso_a_roadmap(
    roadmap_actual: list[dict[str, Any]],
    curso: Optional[dict[str, Any]],
    limite_maximo: int = LIMITE_MAXIMO_ROADMAP_ITEMS,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Agrega un curso publicado al roadmap del usuario.

    Retorna una tupla: (nuevo_item, nuevo_roadmap_actualizado).
    Lanza ReglaNegocioError si:
      - El curso no existe (curso is None o sin id) -> CURSO_NO_ENCONTRADO
      - El curso no está en estado 'publicado' -> CURSO_NO_PUBLICADO
      - El curso ya está en el roadmap -> CURSO_YA_EN_ROADMAP
      - Se excede el límite máximo de ítems -> LIMITE_ROADMAP_ALCANZADO
    """
    if not curso or not curso.get("id"):
        raise ReglaNegocioError(
            codigo="CURSO_NO_ENCONTRADO",
            mensaje="El curso indicado no existe o no tiene un identificador válido.",
        )

    curso_id = curso["id"]
    estado_curso = curso.get("estado")
    if estado_curso != EstadoCurso.PUBLICADO.value and estado_curso != EstadoCurso.PUBLICADO:
        raise ReglaNegocioError(
            codigo="CURSO_NO_PUBLICADO",
            mensaje=f"Solo se pueden agregar al roadmap cursos en estado 'publicado'. Estado actual: '{estado_curso}'.",
        )

    # Verificar unicidad (BR-006: UNIQUE usuario_id, curso_id)
    for item in roadmap_actual:
        if item.get("curso_id") == curso_id:
            raise ReglaNegocioError(
                codigo="CURSO_YA_EN_ROADMAP",
                mensaje="Este curso ya forma parte de tu roadmap.",
            )

    # Verificar límite máximo propio
    if len(roadmap_actual) >= limite_maximo:
        raise ReglaNegocioError(
            codigo="LIMITE_ROADMAP_ALCANZADO",
            mensaje=f"Has alcanzado el límite máximo permitido de {limite_maximo} cursos en tu roadmap.",
        )

    # Asignar orden consecutivo al final
    nuevo_orden = len(roadmap_actual) + 1
    nuevo_item = {
        "id": nuevo_orden,
        "curso_id": curso_id,
        "orden": nuevo_orden,
        "estado": EstadoRoadmapItem.PENDIENTE.value,
        "curso": {
            "id": curso["id"],
            "titulo": curso.get("titulo", ""),
            "tema": curso.get("tema", ""),
            "categoria": curso.get("categoria", ""),
            "url": curso.get("url", ""),
        },
    }

    nuevo_roadmap = [dict(item) for item in roadmap_actual]
    nuevo_roadmap.append(nuevo_item)
    return nuevo_item, nuevo_roadmap


def quitar_curso_de_roadmap(
    roadmap_actual: list[dict[str, Any]],
    curso_id: int,
) -> list[dict[str, Any]]:
    """Elimina un curso del roadmap y recompacta el orden consecutivo.

    Lanza ReglaNegocioError con código ITEM_ROADMAP_NO_ENCONTRADO si no está.
    """
    encontrado = False
    items_restantes: list[dict[str, Any]] = []

    for item in roadmap_actual:
        if item.get("curso_id") == curso_id:
            encontrado = True
        else:
            items_restantes.append(dict(item))

    if not encontrado:
        raise ReglaNegocioError(
            codigo="ITEM_ROADMAP_NO_ENCONTRADO",
            mensaje=f"El curso con ID {curso_id} no se encuentra en el roadmap.",
        )

    # Recompactar órdenes: 1, 2, 3...
    items_reordenados = sorted(items_restantes, key=lambda x: x.get("orden", 0))
    for indice, item in enumerate(items_reordenados, start=1):
        item["orden"] = indice

    return items_reordenados


def reordenar_items_roadmap(
    roadmap_actual: list[dict[str, Any]],
    curso_id: int,
    nuevo_orden: int,
) -> list[dict[str, Any]]:
    """Mueve un curso a una nueva posición dentro del roadmap (1-indexed).

    Ajusta automáticamente el orden de los demás elementos para evitar solapamientos.
    Lanza ReglaNegocioError si:
      - El curso no está en el roadmap -> ITEM_ROADMAP_NO_ENCONTRADO
      - La nueva posición está fuera de rango (1..total) -> ORDEN_FUERA_DE_RANGO
    """
    total_items = len(roadmap_actual)
    if total_items == 0:
        raise ReglaNegocioError(
            codigo="ROADMAP_VACIO",
            mensaje="No hay cursos en el roadmap para reordenar.",
        )

    if nuevo_orden < 1 or nuevo_orden > total_items:
        raise ReglaNegocioError(
            codigo="ORDEN_FUERA_DE_RANGO",
            mensaje=f"El nuevo orden ({nuevo_orden}) debe estar entre 1 y {total_items}.",
        )

    # Buscar el item objetivo
    item_objetivo = None
    resto_items: list[dict[str, Any]] = []
    for item in sorted(roadmap_actual, key=lambda x: x.get("orden", 0)):
        if item.get("curso_id") == curso_id:
            item_objetivo = dict(item)
        else:
            resto_items.append(dict(item))

    if not item_objetivo:
        raise ReglaNegocioError(
            codigo="ITEM_ROADMAP_NO_ENCONTRADO",
            mensaje=f"El curso con ID {curso_id} no se encuentra en el roadmap.",
        )

    # Insertar en la posición deseada (índice 0-based = nuevo_orden - 1)
    resto_items.insert(nuevo_orden - 1, item_objetivo)

    # Recompactar órdenes de todos los elementos
    for indice, item in enumerate(resto_items, start=1):
        item["orden"] = indice

    return resto_items


def cambiar_estado_item_roadmap(
    item: dict[str, Any],
    nuevo_estado: str,
) -> dict[str, Any]:
    """Modifica el estado de progreso de un ítem del roadmap.

    Valores permitidos: 'pendiente', 'en_curso', 'completado'.
    Lanza ReglaNegocioError si el estado es inválido.
    """
    try:
        estado_enum = EstadoRoadmapItem(nuevo_estado)
    except ValueError:
        raise ReglaNegocioError(
            codigo="ESTADO_ROADMAP_INVALIDO",
            mensaje=f"El estado '{nuevo_estado}' no es válido para un ítem del roadmap.",
        )

    item_actualizado = dict(item)
    item_actualizado["estado"] = estado_enum.value
    return item_actualizado
