"""Modelos de datos para el módulo de Catálogo (SQLModel).

Implementa las tablas 'categorias' y 'cursos' según BackendSchema.md §1.2.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class Categoria(SQLModel, table=True):
    """Categoría cerrada de clasificación de cursos."""
    __tablename__ = "categorias"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True, max_length=60)
    descripcion: str = Field(max_length=255)


class Curso(SQLModel, table=True):
    """Curso aportado por la comunidad con ciclo de vida y validación."""
    __tablename__ = "cursos"

    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(unique=True, index=True, max_length=2048)
    titulo: str = Field(max_length=200, index=True)
    tema: str = Field(max_length=150)
    version: str = Field(max_length=50)
    anio_edicion: int = Field(index=True)
    docentes: str = Field(max_length=300)
    tiene_cuestionarios: bool = Field(default=False)
    requiere_examen: bool = Field(default=False)
    extiende_certificado: bool = Field(default=False)
    aval_organizacion_bool: bool = Field(default=False)
    aval_organizacion_nombre: Optional[str] = Field(default=None, max_length=150)
    tomo_el_curso: bool = Field(default=True)
    estado: str = Field(default="en_revision", index=True, max_length=20)
    motivo_rechazo: Optional[str] = Field(default=None)
    categoria_id: int = Field(foreign_key="categorias.id", index=True)
    aporte_usuario_id: int = Field(default=1, index=True)
    revisado_por_id: Optional[int] = Field(default=None)
    revisado_en: Optional[datetime] = Field(default=None)
    creado_en: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
