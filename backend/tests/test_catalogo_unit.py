"""Tests unitarios para las reglas de negocio de catálogo y cursos.

Bloque 1 — Ticket T1.
Patrón AAA (Arrange - Act - Assert) estricto y naming descriptivo:
test_<funcion>_<escenario>_<esperado>
"""
import pytest
from app.catalogo.reglas import (
    EstadoCurso,
    normalizar_url,
    transicionar_estado_curso,
    validar_aporte_curso,
)
from app.compartido.errores import ReglaNegocioError


# ==============================================================================
# 1. Tests de Transiciones de Estado del Curso
# ==============================================================================

def test_transicionar_estado_curso_de_borrador_a_en_revision_exito():
    # Arrange: un curso que se encuentra en borrador
    estado_actual = EstadoCurso.BORRADOR
    nuevo_estado = EstadoCurso.EN_REVISION

    # Act: se solicita la transición hacia en_revision
    estado_resultante, motivo = transicionar_estado_curso(estado_actual, nuevo_estado)

    # Assert: el nuevo estado es en_revision y no tiene motivo de rechazo
    assert estado_resultante == EstadoCurso.EN_REVISION
    assert motivo is None


def test_transicionar_estado_curso_de_en_revision_a_publicado_exito():
    # Arrange: un curso en revisión listo para ser dictaminado por un validador
    estado_actual = EstadoCurso.EN_REVISION
    nuevo_estado = EstadoCurso.PUBLICADO

    # Act: el validador aprueba el curso
    estado_resultante, motivo = transicionar_estado_curso(estado_actual, nuevo_estado)

    # Assert: el curso queda publicado sin motivo de rechazo
    assert estado_resultante == EstadoCurso.PUBLICADO
    assert motivo is None


def test_transicionar_estado_curso_de_en_revision_a_rechazado_con_motivo_exito():
    # Arrange: un curso en revisión y el motivo detallado de rechazo
    estado_actual = EstadoCurso.EN_REVISION
    nuevo_estado = EstadoCurso.RECHAZADO
    motivo_esperado = "El enlace no funciona y el material no es gratuito."

    # Act: el validador rechaza el curso justificando el motivo
    estado_resultante, motivo_obtenido = transicionar_estado_curso(
        estado_actual, nuevo_estado, motivo_rechazo=motivo_esperado
    )

    # Assert: queda rechazado y se preserva el motivo limpio
    assert estado_resultante == EstadoCurso.RECHAZADO
    assert motivo_obtenido == motivo_esperado


def test_transicionar_estado_curso_de_en_revision_a_rechazado_sin_motivo_falla():
    # Arrange: un curso en revisión e intento de rechazo sin motivo
    estado_actual = EstadoCurso.EN_REVISION
    nuevo_estado = EstadoCurso.RECHAZADO
    motivo_vacio = "   "

    # Act & Assert: debe lanzar ReglaNegocioError con código MOTIVO_RECHAZO_REQUERIDO
    with pytest.raises(ReglaNegocioError) as exc_info:
        transicionar_estado_curso(estado_actual, nuevo_estado, motivo_rechazo=motivo_vacio)

    assert exc_info.value.codigo == "MOTIVO_RECHAZO_REQUERIDO"


def test_transicionar_estado_curso_de_publicado_a_en_revision_invalido_falla():
    # Arrange: un curso ya publicado que intenta volver a revisión arbitrariamente
    estado_actual = EstadoCurso.PUBLICADO
    nuevo_estado = EstadoCurso.EN_REVISION

    # Act & Assert: se prohíbe la transición desde publicado
    with pytest.raises(ReglaNegocioError) as exc_info:
        transicionar_estado_curso(estado_actual, nuevo_estado)

    assert exc_info.value.codigo == "TRANSICION_ESTADO_INVALIDA"


def test_transicionar_estado_curso_de_rechazado_a_publicado_directo_falla():
    # Arrange: un curso rechazado que intenta publicarse de forma directa
    estado_actual = EstadoCurso.RECHAZADO
    nuevo_estado = EstadoCurso.PUBLICADO

    # Act & Assert: se prohíbe pasar de rechazado a publicado sin nuevo aporte
    with pytest.raises(ReglaNegocioError) as exc_info:
        transicionar_estado_curso(estado_actual, nuevo_estado)

    assert exc_info.value.codigo == "TRANSICION_ESTADO_INVALIDA"


def test_transicionar_estado_curso_estado_origen_invalido_falla():
    # Arrange: un valor de estado inexistente
    estado_invalido = "estado_inexistente"
    nuevo_estado = EstadoCurso.PUBLICADO

    # Act & Assert: debe lanzar error de estado desconocido
    with pytest.raises(ReglaNegocioError) as exc_info:
        transicionar_estado_curso(estado_invalido, nuevo_estado)

    assert exc_info.value.codigo == "ESTADO_DESCONOCIDO"


# ==============================================================================
# 2. Tests de Validación de Datos de Aporte de Curso
# ==============================================================================

@pytest.fixture
def datos_curso_validos():
    """Fixture con un conjunto completo de datos válidos para un aporte."""
    return {
        "url": "https://plataforma.org/curso-fastapi/",
        "titulo": "FastAPI Profesional y Moderno",
        "tema": "Desarrollo Backend Asíncrono",
        "version": "2026",
        "anio_edicion": 2026,
        "docentes": "Ing. García, Lic. Rossi",
        "categoria_id": 1,
        "tiene_cuestionarios": True,
        "requiere_examen": False,
        "extiende_certificado": True,
        "aval_organizacion_bool": True,
        "aval_organizacion_nombre": "Fundación Código Libre",
        "tomo_el_curso": True,
    }


def test_validar_aporte_curso_camino_feliz_exito(datos_curso_validos):
    # Arrange: datos completos y válidos para el año 2026
    anio_referencia = 2026

    # Act: se valida el aporte
    curso_validado = validar_aporte_curso(datos_curso_validos, anio_actual=anio_referencia)

    # Assert: todos los datos son normalizados y el estado inicial es en_revision
    assert curso_validado["url"] == "https://plataforma.org/curso-fastapi"  # sin barra final redundante
    assert curso_validado["titulo"] == "FastAPI Profesional y Moderno"
    assert curso_validado["estado"] == "en_revision"
    assert curso_validado["aval_organizacion_nombre"] == "Fundación Código Libre"
    assert curso_validado["tomo_el_curso"] is True


def test_validar_aporte_curso_sin_aval_ignora_nombre_exito(datos_curso_validos):
    # Arrange: curso donde aval_organizacion_bool es False pero quedó texto residual
    datos_curso_validos["aval_organizacion_bool"] = False
    datos_curso_validos["aval_organizacion_nombre"] = "Texto que debería limpiarse"

    # Act: se procesa la validación
    curso_validado = validar_aporte_curso(datos_curso_validos, anio_actual=2026)

    # Assert: aval_organizacion_nombre debe quedar en None
    assert curso_validado["aval_organizacion_bool"] is False
    assert curso_validado["aval_organizacion_nombre"] is None


def test_validar_aporte_curso_campo_obligatorio_faltante_falla(datos_curso_validos):
    # Arrange: se remueve el título obligatorio
    datos_curso_validos["titulo"] = "   "

    # Act & Assert: lanza error de campo requerido
    with pytest.raises(ReglaNegocioError) as exc_info:
        validar_aporte_curso(datos_curso_validos, anio_actual=2026)

    assert exc_info.value.codigo == "CAMPO_REQUERIDO"
    assert "titulo" in exc_info.value.mensaje


def test_validar_aporte_curso_url_invalida_falla(datos_curso_validos):
    # Arrange: una URL maliciosa o inválida sin protocolo http/https
    datos_curso_validos["url"] = "ftp://servidor-privado/archivo.zip"

    # Act & Assert: debe rechazar la URL
    with pytest.raises(ReglaNegocioError) as exc_info:
        validar_aporte_curso(datos_curso_validos, anio_actual=2026)

    assert exc_info.value.codigo == "URL_INVALIDA"


def test_validar_aporte_curso_url_duplicada_falla(datos_curso_validos):
    # Arrange: conjunto de URLs ya registradas en la plataforma
    urls_existentes = {"https://plataforma.org/curso-fastapi"}

    # Act & Assert: detecta colisión aún si la nueva viene con mayúsculas o barra final
    datos_curso_validos["url"] = "https://PLATAFORMA.ORG/curso-fastapi/"
    with pytest.raises(ReglaNegocioError) as exc_info:
        validar_aporte_curso(
            datos_curso_validos,
            anio_actual=2026,
            urls_existentes=urls_existentes,
        )

    assert exc_info.value.codigo == "URL_DUPLICADA"


def test_validar_aporte_curso_anio_anterior_a_1990_falla(datos_curso_validos):
    # Arrange: edge case con año 1989 (< límite inferior 1990)
    datos_curso_validos["anio_edicion"] = 1989

    # Act & Assert: debe rechazar el año
    with pytest.raises(ReglaNegocioError) as exc_info:
        validar_aporte_curso(datos_curso_validos, anio_actual=2026)

    assert exc_info.value.codigo == "ANIO_EDICION_INVALIDO"


def test_validar_aporte_curso_anio_futuro_falla(datos_curso_validos):
    # Arrange: edge case con año 2027 siendo el año actual 2026
    anio_actual = 2026
    datos_curso_validos["anio_edicion"] = 2027

    # Act & Assert: no se admiten años futuros
    with pytest.raises(ReglaNegocioError) as exc_info:
        validar_aporte_curso(datos_curso_validos, anio_actual=anio_actual)

    assert exc_info.value.codigo == "ANIO_EDICION_FUTURO"


def test_validar_aporte_curso_anio_limite_exacto_actual_exito(datos_curso_validos):
    # Arrange: edge case donde anio_edicion coincide exactamente con el año actual
    anio_actual = 2026
    datos_curso_validos["anio_edicion"] = 2026

    # Act: validación pura
    resultado = validar_aporte_curso(datos_curso_validos, anio_actual=anio_actual)

    # Assert: es válido y aceptado
    assert resultado["anio_edicion"] == 2026


def test_validar_aporte_curso_sin_declaracion_toma_falla(datos_curso_validos):
    # Arrange: el usuario no marca la declaración jurada de haber tomado el curso
    datos_curso_validos["tomo_el_curso"] = False

    # Act & Assert: lanza error específico de declaración obligatoria (BR-002)
    with pytest.raises(ReglaNegocioError) as exc_info:
        validar_aporte_curso(datos_curso_validos, anio_actual=2026)

    assert exc_info.value.codigo == "DECLARACION_TOMA_REQUERIDA"


def test_transicionar_estado_curso_estado_destino_invalido_falla():
    # Arrange: un estado origen válido pero destino inválido
    estado_actual = EstadoCurso.BORRADOR
    nuevo_invalido = "estado_inexistente"

    # Act & Assert: debe lanzar error de nuevo estado desconocido
    with pytest.raises(ReglaNegocioError) as exc_info:
        transicionar_estado_curso(estado_actual, nuevo_invalido)

    assert exc_info.value.codigo == "ESTADO_DESCONOCIDO"


def test_normalizar_url_cadena_vacia_retorna_vacio():
    # Arrange: URL nula o vacía
    url_vacia = ""

    # Act: se normaliza
    resultado = normalizar_url(url_vacia)

    # Assert: devuelve cadena vacía sin errores
    assert resultado == ""


def test_validar_aporte_curso_anio_no_numerico_falla(datos_curso_validos):
    # Arrange: año con caracteres no convertibles a entero
    datos_curso_validos["anio_edicion"] = "dos_mil_veinte"

    # Act & Assert: lanza error de año inválido
    with pytest.raises(ReglaNegocioError) as exc_info:
        validar_aporte_curso(datos_curso_validos, anio_actual=2026)

    assert exc_info.value.codigo == "ANIO_EDICION_INVALIDO"


def test_validar_aporte_curso_anio_actual_por_defecto_exito(datos_curso_validos):
    # Arrange: se omite anio_actual para que use datetime.now().year
    from datetime import datetime
    datos_curso_validos["anio_edicion"] = datetime.now().year

    # Act: se valida sin pasar anio_actual
    resultado = validar_aporte_curso(datos_curso_validos)

    # Assert: se valida correctamente contra el año actual del sistema
    assert resultado["anio_edicion"] == datetime.now().year


def test_validar_aporte_curso_con_aval_pero_sin_nombre_falla(datos_curso_validos):
    # Arrange: marca aval_organizacion_bool=True pero deja el nombre vacío
    datos_curso_validos["aval_organizacion_bool"] = True
    datos_curso_validos["aval_organizacion_nombre"] = "   "

    # Act & Assert: exige el nombre de la institución
    with pytest.raises(ReglaNegocioError) as exc_info:
        validar_aporte_curso(datos_curso_validos, anio_actual=2026)

    assert exc_info.value.codigo == "AVAL_ORGANIZACION_REQUERIDO"

