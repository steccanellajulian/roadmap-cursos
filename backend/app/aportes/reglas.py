"""Reglas de negocio puras para el servicio de aportes y validación.

Funciones libres de dependencias de infraestructura (sin base de datos, sin HTTP).
Cumplen con los contratos de BackendSchema.md §2 y §3.4.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from app.catalogo.reglas import EstadoCurso
from app.compartido.errores import ReglaNegocioError


class RolUsuario(str, Enum):
    """Roles del sistema según BackendSchema §1.2."""
    ESTUDIANTE = "estudiante"
    VALIDADOR = "validador"


class CodigosErrorAportes:
    """Códigos de error semánticos y estables para desacoplar los tests del texto."""
    PERMISO_DENEGADO = "PERMISO_DENEGADO"
    USUARIO_NO_AUTENTICADO = "USUARIO_NO_AUTENTICADO"
    APORTE_NO_DICTAMINABLE = "APORTE_NO_DICTAMINABLE"
    MOTIVO_REQUERIDO = "MOTIVO_REQUERIDO"
    AUTOVALIDACION_PROHIBIDA = "AUTOVALIDACION_PROHIBIDA"
    APORTE_INVALIDO = "APORTE_INVALIDO"


def verificar_permiso_validador(usuario: Optional[dict[str, Any]]) -> None:
    """Verifica que el usuario tenga rol de validador.

    Lanza ReglaNegocioError con códigos semánticos estables.
    """
    if not usuario or not usuario.get("id"):
        raise ReglaNegocioError(
            codigo=CodigosErrorAportes.USUARIO_NO_AUTENTICADO,
            mensaje="Debe iniciar sesión para realizar esta operación.",
        )

    rol = usuario.get("rol")
    if rol != RolUsuario.VALIDADOR.value and rol != RolUsuario.VALIDADOR:
        raise ReglaNegocioError(
            codigo=CodigosErrorAportes.PERMISO_DENEGADO,
            mensaje="Solo los usuarios con rol 'validador' tienen permisos para dictaminar aportes.",
        )


def dictaminar_aporte(
    aporte: Optional[dict[str, Any]],
    validador: Optional[dict[str, Any]],
    aprobado: bool,
    motivo: Optional[str] = None,
    fecha_revision: Optional[datetime] = None,
) -> dict[str, Any]:
    """Ejecuta de forma pura el dictamen de un aporte por parte de un validador.

    Retorna una copia del aporte con su nuevo estado y metadatos de auditoría.
    Lanza ReglaNegocioError ante infracciones de permisos, estado o reglas de negocio.
    """
    if not aporte or not aporte.get("id"):
        raise ReglaNegocioError(
            codigo=CodigosErrorAportes.APORTE_INVALIDO,
            mensaje="El aporte especificado no es válido o no existe.",
        )

    # 1. Verificar permisos del usuario dictaminador
    verificar_permiso_validador(validador)
    validador_id = validador["id"]

    # 2. Control de conflicto de intereses (no auto-validación)
    aporte_autor_id = aporte.get("aporte_usuario_id")
    if aporte_autor_id is not None and aporte_autor_id == validador_id:
        raise ReglaNegocioError(
            codigo=CodigosErrorAportes.AUTOVALIDACION_PROHIBIDA,
            mensaje="Un usuario no puede dictaminar sus propios aportes por conflicto de intereses.",
        )

    # 3. Solo se pueden dictaminar cursos en estado 'en_revision'
    estado_actual = aporte.get("estado")
    if estado_actual != EstadoCurso.EN_REVISION.value and estado_actual != EstadoCurso.EN_REVISION:
        raise ReglaNegocioError(
            codigo=CodigosErrorAportes.APORTE_NO_DICTAMINABLE,
            mensaje=(
                f"Solo los cursos en estado 'en_revision' admiten dictamen. "
                f"Estado actual: '{estado_actual}'."
            ),
        )

    if fecha_revision is None:
        fecha_revision = datetime.now(timezone.utc)

    # 4. Aplicar dictamen según aprobación o rechazo
    resultado = dict(aporte)
    resultado["revisado_por_id"] = validador_id
    resultado["revisado_en"] = fecha_revision

    if aprobado:
        resultado["estado"] = EstadoCurso.PUBLICADO.value
        resultado["motivo_rechazo"] = None
    else:
        if not motivo or not str(motivo).strip():
            raise ReglaNegocioError(
                codigo=CodigosErrorAportes.MOTIVO_REQUERIDO,
                mensaje="El motivo de rechazo es obligatorio al desestimar un curso.",
            )
        resultado["estado"] = EstadoCurso.RECHAZADO.value
        resultado["motivo_rechazo"] = str(motivo).strip()

    return resultado
