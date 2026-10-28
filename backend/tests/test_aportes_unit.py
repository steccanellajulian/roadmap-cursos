"""Tests unitarios para el servicio puro de Aportes y Validación.

Bloque 1 — Ticket T3.
Patrón AAA (Arrange - Act - Assert) estricto y naming descriptivo:
test_<funcion>_<escenario>_<esperado>

Justificación de diseño de aserciones de error:
Los tests validan códigos de error semánticos constantes (CodigosErrorAportes),
asegurando estabilidad del contrato de API y desacoplamiento frente a cambios
redaccionales o de localización en los mensajes de cara al usuario.
"""
from datetime import datetime, timezone
import pytest
from app.aportes.reglas import (
    CodigosErrorAportes,
    RolUsuario,
    dictaminar_aporte,
    verificar_permiso_validador,
)
from app.catalogo.reglas import EstadoCurso
from app.compartido.errores import ReglaNegocioError


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def usuario_validador():
    return {
        "id": 99,
        "nombre": "Prof. Validador",
        "email": "validador@aprende.local",
        "rol": RolUsuario.VALIDADOR.value,
    }


@pytest.fixture
def usuario_estudiante():
    return {
        "id": 42,
        "nombre": "Lucía Estudiante",
        "email": "lucia@estudiante.utn.edu.ar",
        "rol": RolUsuario.ESTUDIANTE.value,
    }


@pytest.fixture
def aporte_en_revision(usuario_estudiante):
    return {
        "id": 15,
        "titulo": "FastAPI Async Avanzado",
        "url": "https://plataforma.org/fastapi-async",
        "estado": EstadoCurso.EN_REVISION.value,
        "aporte_usuario_id": usuario_estudiante["id"],
        "revisado_por_id": None,
        "revisado_en": None,
        "motivo_rechazo": None,
    }


# ==============================================================================
# 1. Tests de Verificación de Permisos
# ==============================================================================

def test_verificar_permiso_validador_con_rol_validador_exito(usuario_validador):
    # Arrange: un usuario autenticado con rol validador
    usuario = usuario_validador

    # Act & Assert: la verificación no arroja ninguna excepción
    verificar_permiso_validador(usuario)


def test_verificar_permiso_validador_con_rol_estudiante_falla(usuario_estudiante):
    # Arrange: un usuario con rol estudiante que intenta acceder a funciones de moderación
    usuario = usuario_estudiante

    # Act & Assert: lanza error con código semántico PERMISO_DENEGADO
    with pytest.raises(ReglaNegocioError) as exc_info:
        verificar_permiso_validador(usuario)

    assert exc_info.value.codigo == CodigosErrorAportes.PERMISO_DENEGADO


def test_verificar_permiso_validador_sin_autenticacion_falla():
    # Arrange: petición anónima sin usuario en contexto
    usuario_anonimo = None

    # Act & Assert: debe exigir autenticación
    with pytest.raises(ReglaNegocioError) as exc_info:
        verificar_permiso_validador(usuario_anonimo)

    assert exc_info.value.codigo == CodigosErrorAportes.USUARIO_NO_AUTENTICADO


# ==============================================================================
# 2. Tests de Dictamen de Aportes
# ==============================================================================

def test_dictaminar_aporte_aprobar_curso_en_revision_exito(
    aporte_en_revision, usuario_validador
):
    # Arrange: un aporte en revisión y un validador legítimo
    fecha_fijada = datetime(2026, 10, 27, 20, 0, 0, tzinfo=timezone.utc)

    # Act: el validador aprueba el curso
    curso_dictaminado = dictaminar_aporte(
        aporte_en_revision,
        validador=usuario_validador,
        aprobado=True,
        fecha_revision=fecha_fijada,
    )

    # Assert: el curso pasa a publicado, audita el validador y no tiene motivo de rechazo
    assert curso_dictaminado["estado"] == EstadoCurso.PUBLICADO.value
    assert curso_dictaminado["revisado_por_id"] == usuario_validador["id"]
    assert curso_dictaminado["revisado_en"] == fecha_fijada
    assert curso_dictaminado["motivo_rechazo"] is None



def test_dictaminar_aporte_rechazar_con_motivo_exito(
    aporte_en_revision, usuario_validador
):
    # Arrange: un aporte en revisión y el motivo de desestimación
    motivo_escrito = "El curso no es gratuito, solicita suscripción de pago al ingresar."

    # Act: el validador rechaza el aporte brindando el motivo
    curso_dictaminado = dictaminar_aporte(
        aporte_en_revision,
        validador=usuario_validador,
        aprobado=False,
        motivo=motivo_escrito,
    )

    # Assert: queda en estado rechazado con el motivo asentado
    assert curso_dictaminado["estado"] == EstadoCurso.RECHAZADO.value
    assert curso_dictaminado["revisado_por_id"] == usuario_validador["id"]
    assert curso_dictaminado["motivo_rechazo"] == motivo_escrito


def test_dictaminar_aporte_rechazar_sin_motivo_falla(
    aporte_en_revision, usuario_validador
):
    # Arrange: intento de rechazar con motivo en blanco
    motivo_invalido = "   "

    # Act & Assert: lanza error con código semántico MOTIVO_REQUERIDO
    with pytest.raises(ReglaNegocioError) as exc_info:
        dictaminar_aporte(
            aporte_en_revision,
            validador=usuario_validador,
            aprobado=False,
            motivo=motivo_invalido,
        )

    assert exc_info.value.codigo == CodigosErrorAportes.MOTIVO_REQUERIDO


def test_dictaminar_aporte_con_rol_estudiante_falla(
    aporte_en_revision, usuario_estudiante
):
    # Arrange: un estudiante intenta dictaminar un aporte
    # Act & Assert: falla con PERMISO_DENEGADO
    with pytest.raises(ReglaNegocioError) as exc_info:
        dictaminar_aporte(
            aporte_en_revision,
            validador=usuario_estudiante,
            aprobado=True,
        )

    assert exc_info.value.codigo == CodigosErrorAportes.PERMISO_DENEGADO


def test_dictaminar_aporte_no_en_revision_publicado_falla(usuario_validador):
    # Arrange: un curso que ya está publicado
    curso_publicado = {
        "id": 10,
        "estado": EstadoCurso.PUBLICADO.value,
        "aporte_usuario_id": 1,
    }

    # Act & Assert: no permite dictaminar cursos que no estén en revisión
    with pytest.raises(ReglaNegocioError) as exc_info:
        dictaminar_aporte(
            curso_publicado,
            validador=usuario_validador,
            aprobado=True,
        )

    assert exc_info.value.codigo == CodigosErrorAportes.APORTE_NO_DICTAMINABLE


def test_dictaminar_aporte_no_en_revision_rechazado_falla(usuario_validador):
    # Arrange: un curso que ya fue rechazado
    curso_rechazado = {
        "id": 11,
        "estado": EstadoCurso.RECHAZADO.value,
        "aporte_usuario_id": 1,
    }

    # Act & Assert: rechaza redictaminar
    with pytest.raises(ReglaNegocioError) as exc_info:
        dictaminar_aporte(
            curso_rechazado,
            validador=usuario_validador,
            aprobado=True,
        )

    assert exc_info.value.codigo == CodigosErrorAportes.APORTE_NO_DICTAMINABLE


def test_dictaminar_aporte_autovalidacion_conflicto_intereses_falla(usuario_validador):
    # Arrange: aporte creado por el mismo usuario que ahora tiene rol validador
    aporte_propio = {
        "id": 33,
        "estado": EstadoCurso.EN_REVISION.value,
        "aporte_usuario_id": usuario_validador["id"],  # Mismo ID
    }

    # Act & Assert: prohíbe auto-aprobarse por conflicto de intereses
    with pytest.raises(ReglaNegocioError) as exc_info:
        dictaminar_aporte(
            aporte_propio,
            validador=usuario_validador,
            aprobado=True,
        )

    assert exc_info.value.codigo == CodigosErrorAportes.AUTOVALIDACION_PROHIBIDA


def test_dictaminar_aporte_invalido_o_nulo_falla(usuario_validador):
    # Arrange: aporte nulo
    aporte_nulo = None

    # Act & Assert: detecta aporte inválido
    with pytest.raises(ReglaNegocioError) as exc_info:
        dictaminar_aporte(
            aporte_nulo,
            validador=usuario_validador,
            aprobado=True,
        )

    assert exc_info.value.codigo == CodigosErrorAportes.APORTE_INVALIDO
