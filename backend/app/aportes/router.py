"""Router de API REST para el Módulo de Aportes y Validación."""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from app.aportes.reglas import dictaminar_aporte
from app.catalogo.models import Curso
from app.catalogo.reglas import validar_aporte_curso
from app.catalogo.repository import CursoRepository
from app.compartido.database import get_session
from app.compartido.errores import ReglaNegocioError
from app.identidad.seguridad import get_usuario_actual

router = APIRouter(prefix="/api/v1/aportes", tags=["Aportes"])


class AporteCreateSchema(BaseModel):
    url: str
    titulo: str
    tema: str
    version: str
    anio_edicion: int
    docentes: str
    categoria_id: int
    tiene_cuestionarios: bool = False
    requiere_examen: bool = False
    extiende_certificado: bool = False
    aval_organizacion_bool: bool = False
    aval_organizacion_nombre: Optional[str] = None
    tomo_el_curso: bool = True


class ValidarAporteSchema(BaseModel):
    aprobado: bool
    motivo: Optional[str] = None


@router.post("", status_code=status.HTTP_201_CREATED)
def crear_aporte(
    payload: AporteCreateSchema,
    usuario: dict[str, Any] = Depends(get_usuario_actual),
    session: Session = Depends(get_session),
):
    """Crea un nuevo aporte de curso ingresando en estado 'en_revision'."""
    repo = CursoRepository(session)

    # Validar duplicado de URL (BackendSchema §3.4)
    if repo.get_by_url(payload.url):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este curso ya fue aportado.",
        )

    # Validación con funciones puras del dominio
    try:
        datos_validados = validar_aporte_curso(payload.model_dump())
    except ReglaNegocioError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=err.mensaje,
        )

    curso = Curso(
        **datos_validados,
        aporte_usuario_id=usuario["id"],
    )
    curso_guardado = repo.create(curso)

    return {
        "id": curso_guardado.id,
        "estado": curso_guardado.estado,
        "mensaje": "Aporte recibido. Pendiente de validación.",
    }


@router.post("/{aporte_id}/validar")
def dictaminar_aporte_endpoint(
    aporte_id: int,
    payload: ValidarAporteSchema,
    usuario: dict[str, Any] = Depends(get_usuario_actual),
    session: Session = Depends(get_session),
):
    """Dictamina un aporte (aprobar o rechazar con motivo). Requiere rol 'validador'."""
    # 1. Control estricto de rol validador (403 Forbidden)
    if usuario.get("rol") != "validador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permisos para realizar esta acción. Se requiere rol de validador.",
        )

    repo = CursoRepository(session)
    curso = repo.get_by_id(aporte_id)
    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aporte no encontrado.",
        )

    # 2. Ejecutar dictamen puro
    try:
        dictamen = dictaminar_aporte(
            aporte=curso.model_dump(),
            validador=usuario,
            aprobado=payload.aprobado,
            motivo=payload.motivo,
        )
    except ReglaNegocioError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.mensaje,
        )

    # 3. Persistir nuevo estado y campos de auditoría
    curso_actualizado = repo.update(
        aporte_id,
        {
            "estado": dictamen["estado"],
            "revisado_por_id": dictamen["revisado_por_id"],
            "revisado_en": dictamen["revisado_en"],
            "motivo_rechazo": dictamen["motivo_rechazo"],
        },
    )

    return {
        "id": curso_actualizado.id,
        "estado": curso_actualizado.estado,
    }
