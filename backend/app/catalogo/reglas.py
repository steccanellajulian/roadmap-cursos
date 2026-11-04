"""Reglas de negocio puras para el dominio de cursos y catálogo.

Funciones libres de dependencias de infraestructura (sin base de datos, sin HTTP).
Cumplen con los contratos de BackendSchema.md y TRD.md.
"""
from datetime import datetime
from enum import Enum
import re
from typing import Any, Optional, Set

from app.compartido.errores import ReglaNegocioError


class EstadoCurso(str, Enum):
    """Estados del ciclo de vida de un curso según BackendSchema §2."""
    BORRADOR = "borrador"
    EN_REVISION = "en_revision"
    PUBLICADO = "publicado"
    RECHAZADO = "rechazado"


TRANSICIONES_VALIDAS: dict[EstadoCurso, set[EstadoCurso]] = {
    EstadoCurso.BORRADOR: {EstadoCurso.EN_REVISION},
    EstadoCurso.EN_REVISION: {EstadoCurso.PUBLICADO, EstadoCurso.RECHAZADO},
    EstadoCurso.PUBLICADO: set(),
    EstadoCurso.RECHAZADO: set(),
}

PATRON_URL = re.compile(
    r"^https?://"  # http:// o https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # dominio
    r"localhost|"  # localhost
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ip
    r"(?::\d+)?"  # puerto opcional
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


def normalizar_url(url: str) -> str:
    """Normaliza una URL quitando espacios y barra final redundante."""
    if not url:
        return ""
    url_limpia = url.strip()
    if url_limpia.endswith("/") and len(url_limpia) > 8:
        url_limpia = url_limpia[:-1]
    return url_limpia


def transicionar_estado_curso(
    estado_actual: EstadoCurso | str,
    nuevo_estado: EstadoCurso | str,
    motivo_rechazo: Optional[str] = None,
) -> tuple[EstadoCurso, Optional[str]]:
    """Evalúa y ejecuta una transición de estado de curso pura.

    Retorna la tupla (nuevo_estado, motivo_rechazo_limpio).
    Lanza ReglaNegocioError si la transición o los parámetros son inválidos.
    """
    try:
        actual = EstadoCurso(estado_actual)
    except ValueError:
        raise ReglaNegocioError(
            codigo="ESTADO_DESCONOCIDO",
            mensaje=f"El estado actual '{estado_actual}' no es válido.",
        )

    try:
        nuevo = EstadoCurso(nuevo_estado)
    except ValueError:
        raise ReglaNegocioError(
            codigo="ESTADO_DESCONOCIDO",
            mensaje=f"El nuevo estado '{nuevo_estado}' no es válido.",
        )

    if nuevo not in TRANSICIONES_VALIDAS.get(actual, set()):
        raise ReglaNegocioError(
            codigo="TRANSICION_ESTADO_INVALIDA",
            mensaje=(
                f"No se permite transicionar de '{actual.value}' a '{nuevo.value}'."
            ),
        )

    if nuevo == EstadoCurso.RECHAZADO:
        if not motivo_rechazo or not motivo_rechazo.strip():
            raise ReglaNegocioError(
                codigo="MOTIVO_RECHAZO_REQUERIDO",
                mensaje="El motivo de rechazo es obligatorio para rechazar un curso.",
            )
        return (nuevo, motivo_rechazo.strip())

    return (nuevo, None)


def validar_aporte_curso(
    datos: dict[str, Any],
    anio_actual: Optional[int] = None,
    urls_existentes: Optional[Set[str]] = None,
) -> dict[str, Any]:
    """Valida los datos de un aporte de curso según las reglas del dominio.

    Retorna un diccionario de datos normalizado y sanitizado.
    Lanza ReglaNegocioError con código semántico ante cualquier infracción.
    """
    if anio_actual is None:
        anio_actual = datetime.now().year

    # 1. Campos obligatorios de texto y categorías
    campos_obligatorios = [
        "url",
        "titulo",
        "tema",
        "version",
        "anio_edicion",
        "docentes",
        "categoria_id",
    ]
    for campo in campos_obligatorios:
        valor = datos.get(campo)
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ReglaNegocioError(
                codigo="CAMPO_REQUERIDO",
                mensaje=f"El campo '{campo}' es obligatorio.",
                detalles=[{"campo": campo, "mensaje": "Campo obligatorio"}],
            )

    # 2. Validación y normalización de URL
    url_raw = str(datos["url"])
    url_normalizada = normalizar_url(url_raw)
    if not PATRON_URL.match(url_normalizada):
        raise ReglaNegocioError(
            codigo="URL_INVALIDA",
            mensaje="La URL del curso no tiene un formato válido (debe iniciar con http:// o https://).",
            detalles=[{"campo": "url", "mensaje": "Formato de URL inválido"}],
        )

    if urls_existentes:
        urls_limpias = {normalizar_url(u).lower() for u in urls_existentes}
        if url_normalizada.lower() in urls_limpias:
            raise ReglaNegocioError(
                codigo="URL_DUPLICADA",
                mensaje="Este curso ya fue aportado.",
                detalles=[{"campo": "url", "mensaje": "URL ya existente"}],
            )

    # 3. Validación de año de edición
    try:
        anio = int(datos["anio_edicion"])
    except (ValueError, TypeError):
        raise ReglaNegocioError(
            codigo="ANIO_EDICION_INVALIDO",
            mensaje="El año de edición debe ser un número entero.",
            detalles=[{"campo": "anio_edicion", "mensaje": "Debe ser entero"}],
        )

    if anio < 1990:
        raise ReglaNegocioError(
            codigo="ANIO_EDICION_INVALIDO",
            mensaje="El año de edición no puede ser anterior a 1990.",
            detalles=[{"campo": "anio_edicion", "mensaje": "Mínimo 1990"}],
        )

    if anio > anio_actual:
        raise ReglaNegocioError(
            codigo="ANIO_EDICION_FUTURO",
            mensaje="El año de edición no puede ser posterior al año actual.",
            detalles=[
                {
                    "campo": "anio_edicion",
                    "mensaje": f"No puede superar {anio_actual}",
                }
            ],
        )

    # 4. Declaración de toma obligatoria (BR-002)
    tomo_el_curso = bool(datos.get("tomo_el_curso", False))
    if not tomo_el_curso:
        raise ReglaNegocioError(
            codigo="DECLARACION_TOMA_REQUERIDA",
            mensaje="Debe declarar haber tomado el curso para poder aportarlo.",
            detalles=[
                {"campo": "tomo_el_curso", "mensaje": "Declaración obligatoria"}
            ],
        )

    # 5. Aval de organización institucional
    aval_bool = bool(datos.get("aval_organizacion_bool", False))
    aval_nombre = datos.get("aval_organizacion_nombre")
    if aval_bool:
        if not aval_nombre or not str(aval_nombre).strip():
            raise ReglaNegocioError(
                codigo="AVAL_ORGANIZACION_REQUERIDO",
                mensaje="Debe especificar el nombre de la organización que avala el curso.",
                detalles=[
                    {
                        "campo": "aval_organizacion_nombre",
                        "mensaje": "Nombre de entidad requerido",
                    }
                ],
            )
        aval_nombre_limpio = str(aval_nombre).strip()
    else:
        aval_nombre_limpio = None

    # 6. Flags booleanos restantes
    tiene_cuestionarios = bool(datos.get("tiene_cuestionarios", False))
    requiere_examen = bool(datos.get("requiere_examen", False))
    extiende_certificado = bool(datos.get("extiende_certificado", False))

    return {
        "url": url_normalizada,
        "titulo": str(datos["titulo"]).strip(),
        "tema": str(datos["tema"]).strip(),
        "version": str(datos["version"]).strip(),
        "anio_edicion": anio,
        "docentes": str(datos["docentes"]).strip(),
        "categoria_id": int(datos["categoria_id"]),
        "tiene_cuestionarios": tiene_cuestionarios,
        "requiere_examen": requiere_examen,
        "extiende_certificado": extiende_certificado,
        "aval_organizacion_bool": aval_bool,
        "aval_organizacion_nombre": aval_nombre_limpio,
        "tomo_el_curso": tomo_el_curso,
        "estado": EstadoCurso.EN_REVISION.value,
    }
