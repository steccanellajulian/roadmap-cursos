"""
Punto de entrada de la aplicación FastAPI.

Responsabilidad:
Inicializa la API, configura CORS para permitir peticiones desde el frontend,
y expone los endpoints mínimos de salud (/health) y catálogo (/api/v1/cursos).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Aprende-Gratis API",
    description="API del catálogo comunitario de cursos gratuitos y roadmaps de estudio.",
    version="0.1.0",
)

# Permitimos el acceso desde el frontend en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Salud"])
def health():
    """Verifica que el servicio esté levantado y respondiendo."""
    return {"status": "ok"}


@app.get("/api/v1/cursos", tags=["Catálogo"])
@app.get("/cursos", tags=["Catálogo"], include_in_schema=False)
def obtener_cursos():
    """
    Devuelve la lista inicial de cursos del catálogo comunitario.
    Estructura paginada según BackendSchema.md §3.3.
    """
    cursos_ejemplo = [
        {
            "id": 1,
            "titulo": "Python para Principiantes",
            "tema": "Fundamentos del lenguaje y programación estructurada",
            "version": "2026",
            "anio_edicion": 2026,
            "docentes": "Ana Pérez",
            "categoria": {"id": 1, "nombre": "Programación"},
            "tiene_cuestionarios": True,
            "requiere_examen": False,
            "extiende_certificado": True,
            "aval_organizacion": "Comunidad Abierta de Software",
            "tomo_el_curso": True,
            "url": "https://www.youtube.com/watch?v=ejemplo1",
        },
        {
            "id": 2,
            "titulo": "Desarrollo Frontend Moderno",
            "tema": "HTML semántico, CSS responsivo y componentes con React",
            "version": "v19",
            "anio_edicion": 2026,
            "docentes": "Carlos Gómez",
            "categoria": {"id": 2, "nombre": "Desarrollo Web"},
            "tiene_cuestionarios": True,
            "requiere_examen": True,
            "extiende_certificado": True,
            "aval_organizacion": "UTN - Facultad Regional La Plata",
            "tomo_el_curso": True,
            "url": "https://www.youtube.com/watch?v=ejemplo2",
        },
    ]

    return {
        "items": cursos_ejemplo,
        "total": len(cursos_ejemplo),
        "page": 1,
        "page_size": 20,
    }
