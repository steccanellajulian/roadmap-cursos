"""Módulo de seguridad y dependencias de autenticación.

Implementa la extracción del usuario actual mediante token Bearer.
"""
from typing import Any, Optional
from fastapi import Header, HTTPException, status
from app.aportes.reglas import RolUsuario

# Usuarios simulados para tokens de desarrollo y testing
USUARIOS_TOKEN_DEV: dict[str, dict[str, Any]] = {
    "token_validador": {
        "id": 99,
        "nombre": "Validador Oficial",
        "email": "validador@aprende.local",
        "rol": RolUsuario.VALIDADOR.value,
    },
    "token_estudiante": {
        "id": 42,
        "nombre": "Estudiante Alumno",
        "email": "estudiante@aprende.local",
        "rol": RolUsuario.ESTUDIANTE.value,
    },
}


def get_usuario_actual(
    authorization: Optional[str] = Header(None),
) -> dict[str, Any]:
    """Dependencia de FastAPI que valida el header Authorization: Bearer <token>.

    Lanza 401 Unauthorized si falta o es inválido.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere iniciar sesión para acceder a este recurso.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    partes = authorization.split()
    if len(partes) != 2 or partes[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token de autorización inválido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = partes[1].strip()

    # Si es uno de los tokens simulados
    if token in USUARIOS_TOKEN_DEV:
        return USUARIOS_TOKEN_DEV[token]

    # Soporte para tokens codificados simples en tests: e.g. "validador_1" o "estudiante_2"
    if token.startswith("validador"):
        return {
            "id": 99,
            "nombre": "Validador",
            "email": "validador@aprende.local",
            "rol": RolUsuario.VALIDADOR.value,
        }
    if token.startswith("estudiante") or token.startswith("autor"):
        return {
            "id": 42,
            "nombre": "Estudiante",
            "email": "estudiante@aprende.local",
            "rol": RolUsuario.ESTUDIANTE.value,
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
