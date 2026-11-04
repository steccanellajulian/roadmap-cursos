"""Router de API REST para el Catálogo de Cursos."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.catalogo.models import Curso
from app.catalogo.repository import CursoRepository
from app.compartido.database import get_session

router = APIRouter(prefix="/api/v1/cursos", tags=["Catálogo"])


@router.get("")
def listar_cursos_publicados(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=50, description="Tamaño de página"),
    q: Optional[str] = Query(None, description="Término de búsqueda"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    session: Session = Depends(get_session),
):
    """Devuelve el listado paginado de cursos en estado 'publicado'."""
    repo = CursoRepository(session)
    items, total = repo.list_paginated(
        page=page,
        page_size=page_size,
        q=q,
        categoria_id=categoria_id,
        estado="publicado",
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
