"""Tests de integración para CursoRepository con base de datos real.

Bloque 2 — Ticket T4.
Patrón AAA (Arrange - Act - Assert) estricto y naming descriptivo:
test_<funcion>_<escenario>_<esperado>

Justificación de la elección de BD real (SQLite en memoria):
Se utiliza SQLite en memoria (sqlite:///:memory:) como base de datos relacional real.
A diferencia de los mocks o fakes, SQLite es un motor SQL ACID completo que parsea y
ejecuta consultas SQL reales, valida restricciones de tipos, claves foráneas, índices,
ORDER BY, LIMIT y OFFSET.
Beneficios técnicos:
1. Aislamiento total: cada test o módulo arranca con un esquema 100% limpio y efímero.
2. Ejecución determinística y ultra rápida (< 1 segundo para toda la suite).
3. Portabilidad: corre idéntico en desarrollo local, contenedores y CI/CD sin requerir
   un servicio externo ni sockets de red activos.
"""
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.catalogo.models import Categoria, Curso
from app.catalogo.repository import CursoRepository


# ==============================================================================
# Fixtures de Base de Datos Real (SQLite en memoria)
# ==============================================================================

@pytest.fixture(name="session")
def session_fixture():
    """Crea una base de datos SQLite en memoria real con esquema limpio por test."""
    # StaticPool mantiene la base de datos en memoria viva durante la sesión
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Precargar categorías iniciales requeridas por la relación
        cat1 = Categoria(id=1, nombre="Desarrollo Web", descripcion="Cursos web")
        cat2 = Categoria(id=2, nombre="Datos e IA", descripcion="Cursos de datos")
        session.add(cat1)
        session.add(cat2)
        session.commit()
        yield session

    SQLModel.metadata.drop_all(engine)
    engine.dispose()



@pytest.fixture(name="repo")
def repo_fixture(session: Session):
    """Instancia del repositorio conectada a la sesión real de base de datos."""
    return CursoRepository(session)


# ==============================================================================
# 1. Tests CRUD Básicos (Roundtrip create + get_by_id)
# ==============================================================================

def test_create_and_get_by_id_roundtrip_exito(repo: CursoRepository):
    # Arrange: entidad de curso completa lista para ser persistida
    nuevo_curso = Curso(
        url="https://plataforma.org/curso-fastapi",
        titulo="FastAPI Profesional",
        tema="Backend Python",
        version="2026",
        anio_edicion=2026,
        docentes="Ing. García",
        tiene_cuestionarios=True,
        requiere_examen=False,
        extiende_certificado=True,
        aval_organizacion_bool=True,
        aval_organizacion_nombre="UTN",
        tomo_el_curso=True,
        estado="publicado",
        categoria_id=1,
    )

    # Act: se persiste en la BD y se recupera por su clave primaria
    curso_creado = repo.create(nuevo_curso)
    curso_recuperado = repo.get_by_id(curso_creado.id)

    # Assert: roundtrip completo exitoso; los datos persisten idénticos
    assert curso_recuperado is not None
    assert curso_recuperado.id == curso_creado.id
    assert curso_recuperado.url == "https://plataforma.org/curso-fastapi"
    assert curso_recuperado.titulo == "FastAPI Profesional"
    assert curso_recuperado.categoria_id == 1
    assert curso_recuperado.aval_organizacion_nombre == "UTN"


def test_get_by_id_curso_inexistente_retorna_none(repo: CursoRepository):
    # Arrange: un identificador que no existe en la base de datos
    id_inexistente = 9999

    # Act: se busca en la base de datos
    resultado = repo.get_by_id(id_inexistente)

    # Assert: devuelve None sin generar excepciones
    assert resultado is None


# ==============================================================================
# 2. Tests de Paginación (page=1, size=2 -> 2 items; page=2 -> resto; total count)
# ==============================================================================

def test_list_paginated_page1_and_page2_and_total_count_correcto(repo: CursoRepository):
    # Arrange: persistir 5 cursos secuenciales en la base de datos
    for i in range(1, 6):
        repo.create(
            Curso(
                url=f"https://plataforma.org/curso-{i}",
                titulo=f"Curso Número {i}",
                tema="General",
                version="1.0",
                anio_edicion=2026,
                docentes="Docente Test",
                categoria_id=1,
                estado="publicado",
            )
        )

    # Act: solicitar página 1 (tamaño 2), página 2 (tamaño 2) y página 3 (resto)
    items_p1, total_p1 = repo.list_paginated(page=1, page_size=2)
    items_p2, total_p2 = repo.list_paginated(page=2, page_size=2)
    items_p3, total_p3 = repo.list_paginated(page=3, page_size=2)

    # Assert: se verifica tamaño exacto, total_count global y sin solapamiento
    assert total_p1 == 5
    assert total_p2 == 5
    assert total_p3 == 5

    assert len(items_p1) == 2
    assert [c.titulo for c in items_p1] == ["Curso Número 1", "Curso Número 2"]

    assert len(items_p2) == 2
    assert [c.titulo for c in items_p2] == ["Curso Número 3", "Curso Número 4"]

    assert len(items_p3) == 1
    assert [c.titulo for c in items_p3] == ["Curso Número 5"]


# ==============================================================================
# 3. Tests de Filtro de Búsqueda q (parcial y case-insensitive) y Categoría
# ==============================================================================

def test_list_paginated_filtro_q_parcial_y_case_insensitive(repo: CursoRepository):
    # Arrange: persistir cursos con diferentes títulos y temas
    repo.create(
        Curso(
            url="https://p1.org",
            titulo="Python para Principiantes",
            tema="Programación",
            version="1.0",
            anio_edicion=2026,
            docentes="A",
            categoria_id=1,
        )
    )
    repo.create(
        Curso(
            url="https://p2.org",
            titulo="Desarrollo Web Moderno",
            tema="Fundamentos de PYTHON en Web",
            version="1.0",
            anio_edicion=2026,
            docentes="B",
            categoria_id=1,
        )
    )
    repo.create(
        Curso(
            url="https://p3.org",
            titulo="Introducción a Docker",
            tema="Contenedores",
            version="1.0",
            anio_edicion=2026,
            docentes="C",
            categoria_id=2,
        )
    )

    # Act: búsqueda en minúsculas 'python' y en mayúsculas 'PYTHON'
    items_minusc, total_minusc = repo.list_paginated(q="python")
    items_mayusc, total_mayusc = repo.list_paginated(q="PYTHON")
    items_docker, total_docker = repo.list_paginated(q="dock")

    # Assert: coincide parcialmente en título o tema sin importar mayúsculas
    assert total_minusc == 2
    assert total_mayusc == 2
    assert {c.url for c in items_minusc} == {"https://p1.org", "https://p2.org"}

    assert total_docker == 1
    assert items_docker[0].titulo == "Introducción a Docker"


def test_list_paginated_filtro_por_categoria(repo: CursoRepository):
    # Arrange: cursos distribuidos en categoría 1 y categoría 2
    repo.create(
        Curso(
            url="https://c1.org",
            titulo="Curso Cat 1",
            tema="Web",
            version="1.0",
            anio_edicion=2026,
            docentes="Doc 1",
            categoria_id=1,
        )
    )
    repo.create(
        Curso(
            url="https://c2.org",
            titulo="Curso Cat 2",
            tema="IA",
            version="1.0",
            anio_edicion=2026,
            docentes="Doc 2",
            categoria_id=2,
        )
    )

    # Act: filtrar por categoría 1
    items_cat1, total_cat1 = repo.list_paginated(categoria_id=1)
    # Act: filtrar por categoría 2
    items_cat2, total_cat2 = repo.list_paginated(categoria_id=2)

    # Assert: solo devuelve registros de la categoría indicada
    assert total_cat1 == 1
    assert items_cat1[0].categoria_id == 1

    assert total_cat2 == 1
    assert items_cat2[0].categoria_id == 2


# ==============================================================================
# 4. Tests de Update Parcial y Delete (delete y get_by_id -> None)
# ==============================================================================

def test_update_campos_parciales_exito(repo: CursoRepository):
    # Arrange: un curso guardado en la base de datos
    curso_original = repo.create(
        Curso(
            url="https://original.org",
            titulo="Título Original",
            tema="Tema Original",
            version="1.0",
            anio_edicion=2025,
            docentes="Docente Original",
            categoria_id=1,
            estado="en_revision",
        )
    )

    # Act: se actualizan solo el título y la versión
    curso_actualizado = repo.update(
        curso_original.id,
        {"titulo": "Título Actualizado", "version": "2.0"},
    )

    # Assert: los campos modificados cambian, y el resto se conserva intacto
    assert curso_actualizado is not None
    assert curso_actualizado.titulo == "Título Actualizado"
    assert curso_actualizado.version == "2.0"
    assert curso_actualizado.url == "https://original.org"
    assert curso_actualizado.tema == "Tema Original"
    assert curso_actualizado.anio_edicion == 2025


def test_update_curso_inexistente_retorna_none(repo: CursoRepository):
    # Arrange: ID de curso que no existe
    id_falso = 8888

    # Act: intento de actualización
    resultado = repo.update(id_falso, {"titulo": "Nuevo"})

    # Assert: devuelve None
    assert resultado is None


def test_delete_y_get_by_id_retorna_none(repo: CursoRepository):
    # Arrange: un curso persistido en la base de datos
    curso = repo.create(
        Curso(
            url="https://para-borrar.org",
            titulo="Curso a Borrar",
            tema="Temporal",
            version="1.0",
            anio_edicion=2026,
            docentes="Docente",
            categoria_id=1,
        )
    )
    curso_id = curso.id

    # Act: se ejecuta la eliminación
    eliminado_exitoso = repo.delete(curso_id)
    curso_consultado = repo.get_by_id(curso_id)

    # Assert: delete devuelve True y subsequent get_by_id devuelve None
    assert eliminado_exitoso is True
    assert curso_consultado is None


def test_get_by_url_exito(repo: CursoRepository):
    # Arrange: un curso guardado con su URL
    repo.create(
        Curso(
            url="https://plataforma.org/url-especifica",
            titulo="Curso URL",
            tema="Test",
            version="1.0",
            anio_edicion=2026,
            docentes="Doc",
            categoria_id=1,
        )
    )

    # Act: buscar por URL
    curso_encontrado = repo.get_by_url("https://plataforma.org/url-especifica")
    curso_no_encontrado = repo.get_by_url("https://no-existe.org")

    # Assert: recupera el curso exacto y None si no existe
    assert curso_encontrado is not None
    assert curso_encontrado.titulo == "Curso URL"
    assert curso_no_encontrado is None


def test_list_paginated_filtro_por_estado(repo: CursoRepository):
    # Arrange: un curso publicado y uno en revisión
    repo.create(
        Curso(
            url="https://c-pub.org",
            titulo="Publicado",
            tema="T",
            version="1.0",
            anio_edicion=2026,
            docentes="D",
            categoria_id=1,
            estado="publicado",
        )
    )
    repo.create(
        Curso(
            url="https://c-rev.org",
            titulo="En Revisión",
            tema="T",
            version="1.0",
            anio_edicion=2026,
            docentes="D",
            categoria_id=1,
            estado="en_revision",
        )
    )

    # Act: filtrar solo publicados
    items_publicados, total_pub = repo.list_paginated(estado="publicado")

    # Assert: solo devuelve el publicado
    assert total_pub == 1
    assert items_publicados[0].titulo == "Publicado"


def test_delete_curso_inexistente_retorna_false(repo: CursoRepository):
    # Arrange: ID inexistente
    id_falso = 7777

    # Act: intento de borrado
    resultado = repo.delete(id_falso)

    # Assert: devuelve False
    assert resultado is False

