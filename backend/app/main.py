"""Punto de entrada de la aplicación FastAPI.

Inicializa la API, configura CORS y monta los routers de Catálogo y Aportes.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.aportes.router import router as aportes_router
from app.catalogo.router import router as catalogo_router

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

# Registrar routers de módulos
app.include_router(catalogo_router)
app.include_router(aportes_router)


@app.get("/health", tags=["Salud"])
def health():
    """Verifica que el servicio esté levantado y respondiendo."""
    return {"status": "ok"}
