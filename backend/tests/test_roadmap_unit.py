"""Tests unitarios para las reglas de negocio del Roadmap Personal.

Bloque 1 — Ticket T2.
Patrón AAA (Arrange - Act - Assert) estricto y naming descriptivo:
test_<funcion>_<escenario>_<esperado>
"""
import pytest
from app.catalogo.reglas import EstadoCurso
from app.compartido.errores import ReglaNegocioError
from app.roadmap.reglas import (
    EstadoRoadmapItem,
    agregar_curso_a_roadmap,
    cambiar_estado_item_roadmap,
    quitar_curso_de_roadmap,
    reordenar_items_roadmap,
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def curso_publicado_1():
    return {
        "id": 101,
        "titulo": "Python desde Cero",
        "tema": "Programación",
        "categoria": "Desarrollo de Software",
        "url": "https://plataforma.org/python",
        "estado": EstadoCurso.PUBLICADO.value,
    }


@pytest.fixture
def curso_publicado_2():
    return {
        "id": 102,
        "titulo": "FastAPI Avanzado",
        "tema": "Backend",
        "categoria": "Desarrollo de Software",
        "url": "https://plataforma.org/fastapi",
        "estado": EstadoCurso.PUBLICADO.value,
    }


@pytest.fixture
def curso_publicado_3():
    return {
        "id": 103,
        "titulo": "Docker y Kubernetes",
        "tema": "DevOps",
        "categoria": "Infraestructura",
        "url": "https://plataforma.org/docker",
        "estado": EstadoCurso.PUBLICADO.value,
    }


@pytest.fixture
def roadmap_tres_items(curso_publicado_1, curso_publicado_2, curso_publicado_3):
    return [
        {
            "id": 1,
            "curso_id": curso_publicado_1["id"],
            "orden": 1,
            "estado": EstadoRoadmapItem.PENDIENTE.value,
            "curso": curso_publicado_1,
        },
        {
            "id": 2,
            "curso_id": curso_publicado_2["id"],
            "orden": 2,
            "estado": EstadoRoadmapItem.EN_CURSO.value,
            "curso": curso_publicado_2,
        },
        {
            "id": 3,
            "curso_id": curso_publicado_3["id"],
            "orden": 3,
            "estado": EstadoRoadmapItem.PENDIENTE.value,
            "curso": curso_publicado_3,
        },
    ]


# ==============================================================================
# 1. Tests de Agregar Curso al Roadmap
# ==============================================================================

def test_agregar_curso_a_roadmap_curso_publicado_exito(curso_publicado_1):
    # Arrange: un roadmap vacío y un curso válido en estado publicado
    roadmap_inicial = []

    # Act: el usuario agrega el curso a su roadmap
    nuevo_item, nuevo_roadmap = agregar_curso_a_roadmap(roadmap_inicial, curso_publicado_1)

    # Assert: el curso se añade con orden 1 y estado inicial pendiente
    assert nuevo_item["curso_id"] == 101
    assert nuevo_item["orden"] == 1
    assert nuevo_item["estado"] == EstadoRoadmapItem.PENDIENTE.value
    assert len(nuevo_roadmap) == 1


def test_agregar_curso_a_roadmap_curso_no_publicado_falla():
    # Arrange: un curso que todavía se encuentra en_revision (BR-003)
    curso_en_revision = {
        "id": 202,
        "titulo": "Bases de Datos SQL",
        "estado": EstadoCurso.EN_REVISION.value,
    }
    roadmap_actual = []

    # Act & Assert: debe lanzar error impidiendo agregar cursos no publicados
    with pytest.raises(ReglaNegocioError) as exc_info:
        agregar_curso_a_roadmap(roadmap_actual, curso_en_revision)

    assert exc_info.value.codigo == "CURSO_NO_PUBLICADO"


def test_agregar_curso_a_roadmap_curso_inexistente_falla():
    # Arrange: referencia a un curso None o sin identificador
    curso_invalido = None
    roadmap_actual = []

    # Act & Assert: lanza error de curso no encontrado
    with pytest.raises(ReglaNegocioError) as exc_info:
        agregar_curso_a_roadmap(roadmap_actual, curso_invalido)

    assert exc_info.value.codigo == "CURSO_NO_ENCONTRADO"


def test_agregar_curso_a_roadmap_curso_duplicado_falla(curso_publicado_1):
    # Arrange: un roadmap que ya contiene al curso 101 (BR-006)
    roadmap_con_curso = [
        {"id": 1, "curso_id": 101, "orden": 1, "estado": EstadoRoadmapItem.PENDIENTE.value}
    ]

    # Act & Assert: se prohíbe duplicar el mismo curso en el roadmap
    with pytest.raises(ReglaNegocioError) as exc_info:
        agregar_curso_a_roadmap(roadmap_con_curso, curso_publicado_1)

    assert exc_info.value.codigo == "CURSO_YA_EN_ROADMAP"


def test_agregar_curso_a_roadmap_limite_maximo_alcanzado_falla(curso_publicado_2):
    # Arrange: un roadmap que ya alcanzó el límite permitido (ej. límite = 2)
    roadmap_lleno = [
        {"id": 1, "curso_id": 901, "orden": 1, "estado": EstadoRoadmapItem.COMPLETADO.value},
        {"id": 2, "curso_id": 902, "orden": 2, "estado": EstadoRoadmapItem.EN_CURSO.value},
    ]

    # Act & Assert: se rechaza al superar el límite configurado
    with pytest.raises(ReglaNegocioError) as exc_info:
        agregar_curso_a_roadmap(roadmap_lleno, curso_publicado_2, limite_maximo=2)

    assert exc_info.value.codigo == "LIMITE_ROADMAP_ALCANZADO"


# ==============================================================================
# 2. Tests de Quitar Curso del Roadmap
# ==============================================================================

def test_quitar_curso_de_roadmap_existente_recompacta_ordenes_exito(roadmap_tres_items):
    # Arrange: roadmap con 3 cursos (IDs: 101, 102, 103 con ordenes 1, 2, 3)
    curso_a_quitar = 102  # se quita el del medio (orden 2)

    # Act: se elimina el curso del medio
    resultado = quitar_curso_de_roadmap(roadmap_tres_items, curso_id=curso_a_quitar)

    # Assert: quedan 2 items y sus órdenes se recompactan a 1 y 2
    assert len(resultado) == 2
    assert resultado[0]["curso_id"] == 101
    assert resultado[0]["orden"] == 1
    assert resultado[1]["curso_id"] == 103
    assert resultado[1]["orden"] == 2


def test_quitar_curso_de_roadmap_inexistente_falla(roadmap_tres_items):
    # Arrange: solicitud para quitar un curso que no está en el roadmap
    curso_inexistente = 999

    # Act & Assert: debe lanzar error de item no encontrado
    with pytest.raises(ReglaNegocioError) as exc_info:
        quitar_curso_de_roadmap(roadmap_tres_items, curso_id=curso_inexistente)

    assert exc_info.value.codigo == "ITEM_ROADMAP_NO_ENCONTRADO"


# ==============================================================================
# 3. Tests de Reordenar Cursos en el Roadmap
# ==============================================================================

def test_reordenar_items_roadmap_mover_al_inicio_exito(roadmap_tres_items):
    # Arrange: cursos 101(orden 1), 102(orden 2), 103(orden 3)
    curso_a_mover = 103
    nuevo_orden_deseado = 1

    # Act: se mueve el curso 103 a la primera posición
    roadmap_reordenado = reordenar_items_roadmap(
        roadmap_tres_items, curso_id=curso_a_mover, nuevo_orden=nuevo_orden_deseado
    )

    # Assert: ahora el curso 103 tiene orden 1, y los demás se desplazan
    assert [item["curso_id"] for item in roadmap_reordenado] == [103, 101, 102]
    assert [item["orden"] for item in roadmap_reordenado] == [1, 2, 3]


def test_reordenar_items_roadmap_mover_al_final_exito(roadmap_tres_items):
    # Arrange: cursos 101(orden 1), 102(orden 2), 103(orden 3)
    curso_a_mover = 101
    nuevo_orden_deseado = 3

    # Act: se mueve el primer curso al final
    roadmap_reordenado = reordenar_items_roadmap(
        roadmap_tres_items, curso_id=curso_a_mover, nuevo_orden=nuevo_orden_deseado
    )

    # Assert: el curso 101 queda en el puesto 3
    assert [item["curso_id"] for item in roadmap_reordenado] == [102, 103, 101]
    assert [item["orden"] for item in roadmap_reordenado] == [1, 2, 3]


def test_reordenar_items_roadmap_orden_fuera_de_rango_menor_a_uno_falla(roadmap_tres_items):
    # Arrange: intento de asignar orden 0
    orden_invalido = 0

    # Act & Assert: lanza error de orden fuera de rango
    with pytest.raises(ReglaNegocioError) as exc_info:
        reordenar_items_roadmap(roadmap_tres_items, curso_id=101, nuevo_orden=orden_invalido)

    assert exc_info.value.codigo == "ORDEN_FUERA_DE_RANGO"


def test_reordenar_items_roadmap_orden_fuera_de_rango_mayor_al_total_falla(roadmap_tres_items):
    # Arrange: intento de asignar orden 4 en una lista de 3 elementos
    orden_excedido = 4

    # Act & Assert: lanza error de orden fuera de rango
    with pytest.raises(ReglaNegocioError) as exc_info:
        reordenar_items_roadmap(roadmap_tres_items, curso_id=101, nuevo_orden=orden_excedido)

    assert exc_info.value.codigo == "ORDEN_FUERA_DE_RANGO"


def test_reordenar_items_roadmap_en_lista_vacia_falla():
    # Arrange: roadmap sin cursos
    roadmap_vacio = []

    # Act & Assert: no es posible reordenar un roadmap vacío
    with pytest.raises(ReglaNegocioError) as exc_info:
        reordenar_items_roadmap(roadmap_vacio, curso_id=101, nuevo_orden=1)

    assert exc_info.value.codigo == "ROADMAP_VACIO"


def test_reordenar_items_roadmap_curso_no_encontrado_falla(roadmap_tres_items):
    # Arrange: ID de curso inexistente en la lista
    curso_no_encontrado = 999

    # Act & Assert: lanza error de ítem no encontrado
    with pytest.raises(ReglaNegocioError) as exc_info:
        reordenar_items_roadmap(roadmap_tres_items, curso_id=curso_no_encontrado, nuevo_orden=1)

    assert exc_info.value.codigo == "ITEM_ROADMAP_NO_ENCONTRADO"


# ==============================================================================
# 4. Tests de Cambiar Estado de Avance en Roadmap
# ==============================================================================

def test_cambiar_estado_item_roadmap_a_en_curso_exito():
    # Arrange: un item actualmente en pendiente
    item_inicial = {
        "id": 1,
        "curso_id": 101,
        "orden": 1,
        "estado": EstadoRoadmapItem.PENDIENTE.value,
    }

    # Act: el estudiante comienza el curso
    item_actualizado = cambiar_estado_item_roadmap(
        item_inicial, nuevo_estado=EstadoRoadmapItem.EN_CURSO.value
    )

    # Assert: el estado pasa a en_curso
    assert item_actualizado["estado"] == EstadoRoadmapItem.EN_CURSO.value


def test_cambiar_estado_item_roadmap_a_completado_exito():
    # Arrange: un item actualmente en progreso
    item_inicial = {
        "id": 1,
        "curso_id": 101,
        "orden": 1,
        "estado": EstadoRoadmapItem.EN_CURSO.value,
    }

    # Act: el estudiante completa el curso
    item_actualizado = cambiar_estado_item_roadmap(
        item_inicial, nuevo_estado=EstadoRoadmapItem.COMPLETADO.value
    )

    # Assert: el estado queda completado
    assert item_actualizado["estado"] == EstadoRoadmapItem.COMPLETADO.value


def test_cambiar_estado_item_roadmap_estado_invalido_falla():
    # Arrange: estado inventado que no pertenece al enum
    item_inicial = {
        "id": 1,
        "curso_id": 101,
        "orden": 1,
        "estado": EstadoRoadmapItem.PENDIENTE.value,
    }
    estado_invalido = "abandonado_temporalmente"

    # Act & Assert: lanza error de estado inválido
    with pytest.raises(ReglaNegocioError) as exc_info:
        cambiar_estado_item_roadmap(item_inicial, nuevo_estado=estado_invalido)

    assert exc_info.value.codigo == "ESTADO_ROADMAP_INVALIDO"
