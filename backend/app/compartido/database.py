"""Configuración de base de datos y sesión para FastAPI."""
import os
from typing import Generator
from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./aprende_gratis.db",
)

# En SQLite necesitamos check_same_thread=False
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def init_db() -> None:
    """Crea las tablas en la base de datos si no existen."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Generador de sesiones de base de datos inyectable en FastAPI."""
    with Session(engine) as session:
        yield session
