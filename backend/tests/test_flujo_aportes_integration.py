"""Tests de integración para el flujo completo de Aporte y Validación.

Bloque 2 — Ticket T5.
Patrón AAA (Arrange - Act - Assert) estricto y naming descriptivo:
test_<funcion>_<escenario>_<esperado>
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.catalogo.models import Categoria
from app.compartido.database import get_session
from app.main import app


# ==============================================================================
# Fixtures de Base de Datos Real y TestClient
# ==============================================================================

@pytest.fixture(name="client")
def client_fixture():
    """Configura un TestClient conectado a una base de datos SQLite en memoria real."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_test_session():
        with Session(engine) as session:
            yield session

    # Precargar categorías iniciales
    with Session(engine) as session:
        cat1 = Categoria(id=1, nombre="Programación", descripcion="Cursos de código")
        session.add(cat1)
        session.commit()

    app.dependency_overrides[get_session] = get_test_session
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def payload_aporte_valido():
    return {
        "url": "https://plataforma.org/curso-fastapi",
        "titulo": "FastAPI REST Profesional",
        "tema": "Desarrollo Backend",
        "version": "2026",
        "anio_edicion": 2026,
        "docentes": "Ing. García",
        "categoria_id": 1,
        "tiene_cuestionarios": True,
        "requiere_examen": False,
        "extiende_certificado": True,
        "aval_organizacion_bool": False,
        "tomo_el_curso": True,
    }


# ==============================================================================
# 1. Tests del Flujo Aporte -> Estado en_revision
# ==============================================================================

def test_aporte_valido_crea_curso_en_estado_en_revision(
    client: TestClient, payload_aporte_valido: dict
):
    # Arrange: usuario estudiante con sesión iniciada
    headers_autor = {"Authorization": "Bearer token_estudiante"}

    # Act: el autor envía su aporte
    response = client.post("/api/v1/aportes", json=payload_aporte_valido, headers=headers_autor)

    # Assert: estado 201 Created y el curso ingresa en estado 'en_revision'
    assert response.status_code == 201
    datos = response.json()
    assert datos["estado"] == "en_revision"
    assert datos["id"] > 0
    assert "Aporte recibido" in datos["mensaje"]


# ==============================================================================
# 2. Tests de Aprobación -> Curso Publicado y Visible en Catálogo
# ==============================================================================

def test_validar_aprobado_publica_curso_y_lo_hace_visible_en_catalogo(
    client: TestClient, payload_aporte_valido: dict
):
    # Arrange: un aporte recién creado en revisión
    headers_autor = {"Authorization": "Bearer token_estudiante"}
    resp_crear = client.post("/api/v1/aportes", json=payload_aporte_valido, headers=headers_autor)
    curso_id = resp_crear.json()["id"]

    # Verificar que inicialmente NO es visible en el catálogo público
    resp_cat_inicial = client.get("/api/v1/cursos")
    assert resp_cat_inicial.status_code == 200
    assert resp_cat_inicial.json()["total"] == 0

    # Act: un usuario validador aprueba el curso
    headers_validador = {"Authorization": "Bearer token_validador"}
    resp_dictamen = client.post(
        f"/api/v1/aportes/{curso_id}/validar",
        json={"aprobado": True},
        headers=headers_validador,
    )

    # Assert 1: el endpoint de validación devuelve estado publicado
    assert resp_dictamen.status_code == 200
    assert resp_dictamen.json()["estado"] == "publicado"

    # Assert 2: ahora el curso sí aparece en el listado público del catálogo
    resp_cat_final = client.get("/api/v1/cursos")
    assert resp_cat_final.status_code == 200
    data_cat = resp_cat_final.json()
    assert data_cat["total"] == 1
    assert data_cat["items"][0]["id"] == curso_id
    assert data_cat["items"][0]["titulo"] == "FastAPI REST Profesional"


# ==============================================================================
# 3. Tests de Rechazo -> Curso NO Visible en Catálogo
# ==============================================================================

def test_validar_rechazado_no_es_visible_en_catalogo(
    client: TestClient, payload_aporte_valido: dict
):
    # Arrange: un aporte enviado a revisión
    headers_autor = {"Authorization": "Bearer token_estudiante"}
    resp_crear = client.post("/api/v1/aportes", json=payload_aporte_valido, headers=headers_autor)
    curso_id = resp_crear.json()["id"]

    # Act: el validador rechaza el aporte fundamentando el motivo
    headers_validador = {"Authorization": "Bearer token_validador"}
    resp_rechazo = client.post(
        f"/api/v1/aportes/{curso_id}/validar",
        json={"aprobado": False, "motivo": "El material no es gratuito ni abierto."},
        headers=headers_validador,
    )

    # Assert 1: el estado queda asentado en 'rechazado'
    assert resp_rechazo.status_code == 200
    assert resp_rechazo.json()["estado"] == "rechazado"

    # Assert 2: el catálogo público no muestra el curso
    resp_catalogo = client.get("/api/v1/cursos")
    assert resp_catalogo.status_code == 200
    assert resp_catalogo.json()["total"] == 0


# ==============================================================================
# 4. Tests de Permisos (Validador sin rol -> 403; Autor sin sesión -> 401)
# ==============================================================================

def test_permisos_validador_sin_rol_validador_devuelve_403(
    client: TestClient, payload_aporte_valido: dict
):
    # Arrange: un aporte creado y un usuario que tiene sesión pero su rol es estudiante
    headers_estudiante = {"Authorization": "Bearer token_estudiante"}
    resp_crear = client.post("/api/v1/aportes", json=payload_aporte_valido, headers=headers_estudiante)
    curso_id = resp_crear.json()["id"]

    # Act: el estudiante intenta dictaminar el curso
    resp_dictamen = client.post(
        f"/api/v1/aportes/{curso_id}/validar",
        json={"aprobado": True},
        headers=headers_estudiante,
    )

    # Assert: debe denegar el acceso con HTTP 403 Forbidden
    assert resp_dictamen.status_code == 403
    assert "rol de validador" in resp_dictamen.json()["detail"]


def test_permisos_autor_sin_sesion_devuelve_401(
    client: TestClient, payload_aporte_valido: dict
):
    # Arrange: petición sin header Authorization
    # Act: intento de aportar sin haber iniciado sesión
    response = client.post("/api/v1/aportes", json=payload_aporte_valido)

    # Assert: debe responder con HTTP 401 Unauthorized
    assert response.status_code == 401
    assert "iniciar sesión" in response.json()["detail"]
