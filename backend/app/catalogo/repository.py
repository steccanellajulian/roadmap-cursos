"""Repositorio de datos para el Catálogo de Cursos.

Implementa el acceso a datos mediante SQLModel/SQLAlchemy para la entidad Curso.
Soporta CRUD completo, paginación con total count y filtros multicriterio.
"""
from typing import Any, Optional
from sqlmodel import Session, col, func, or_, select
from app.catalogo.models import Curso


class CursoRepository:
    """Única puerta de acceso a la persistencia de cursos en base de datos."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, curso: Curso) -> Curso:
        """Persiste un nuevo curso en la base de datos."""
        self.session.add(curso)
        self.session.commit()
        self.session.refresh(curso)
        return curso

    def get_by_id(self, curso_id: int) -> Optional[Curso]:
        """Obtiene un curso por su ID de clave primaria."""
        return self.session.get(Curso, curso_id)

    def get_by_url(self, url: str) -> Optional[Curso]:
        """Busca un curso por su URL única."""
        statement = select(Curso).where(Curso.url == url)
        return self.session.exec(statement).first()

    def list_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        q: Optional[str] = None,
        categoria_id: Optional[int] = None,
        estado: Optional[str] = None,
    ) -> tuple[list[Curso], int]:
        """Lista cursos de forma paginada con filtros de búsqueda y categoría.

        Retorna (items, total_count).
        q: búsqueda parcial e insensible a mayúsculas/minúsculas en título o tema.
        categoria_id: filtro exacto por categoría.
        estado: filtro por estado (por defecto opcional).
        """
        # Consulta base
        conditions = []

        if estado is not None:
            conditions.append(Curso.estado == estado)

        if categoria_id is not None:
            conditions.append(Curso.categoria_id == categoria_id)

        if q and q.strip():
            filtro_q = f"%{q.strip()}%"
            conditions.append(
                or_(
                    col(Curso.titulo).ilike(filtro_q),
                    col(Curso.tema).ilike(filtro_q),
                )
            )

        # 1. Total count
        count_stmt = select(func.count(Curso.id))
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        total: int = self.session.exec(count_stmt).one()

        # 2. Paginación con offset y limit
        offset = max(0, (page - 1) * page_size)
        query_stmt = select(Curso)
        if conditions:
            query_stmt = query_stmt.where(*conditions)
        query_stmt = query_stmt.order_by(Curso.id).offset(offset).limit(page_size)

        items = list(self.session.exec(query_stmt).all())
        return items, total

    def update(self, curso_id: int, datos: dict[str, Any]) -> Optional[Curso]:
        """Actualiza campos parciales de un curso existente."""
        curso = self.get_by_id(curso_id)
        if not curso:
            return None

        for campo, valor in datos.items():
            if hasattr(curso, campo) and campo != "id":
                setattr(curso, campo, valor)

        self.session.add(curso)
        self.session.commit()
        self.session.refresh(curso)
        return curso

    def delete(self, curso_id: int) -> bool:
        """Elimina un curso por su ID. Retorna True si se eliminó, False si no existía."""
        curso = self.get_by_id(curso_id)
        if not curso:
            return False

        self.session.delete(curso)
        self.session.commit()
        return True
