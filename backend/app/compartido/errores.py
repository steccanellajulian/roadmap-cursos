"""Módulo de excepciones y errores de dominio compartido."""
from typing import Any, Optional


class ReglaNegocioError(Exception):
    """Excepción base para violaciones de reglas de negocio en el dominio."""

    def __init__(
        self,
        codigo: str,
        mensaje: str,
        detalles: Optional[list[dict[str, Any]]] = None,
    ):
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje
        self.detalles = detalles

    def to_dict(self) -> dict[str, Any]:
        """Serializa el error según el envelope estándar del TRD (TD-003)."""
        return {
            "error": {
                "code": self.codigo,
                "message": self.mensaje,
                "details": self.detalles,
            }
        }
