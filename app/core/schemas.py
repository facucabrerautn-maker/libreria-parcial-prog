"""DTO base compartido por las actualizaciones parciales (PATCH).

Los DTO `*Update` permiten omitir campos, pero no aceptar `null` en columnas
que la base declara NOT NULL. Un `null` explícito es un dato inválido (422),
no una actualización parcial: si se dejara pasar, la escritura terminaría en
un IntegrityError traducido a un 409 engañoso (o en un 500).
"""

from typing import Any, ClassVar

from pydantic import model_validator
from sqlmodel import SQLModel


class UpdateModel(SQLModel):
    """Base de los DTO de PATCH parcial.

    Cada subclase declara en `campos_no_nulos` las columnas que no admiten
    `null` explícito. Omitir el campo deja el valor actual; enviarlo como
    `null` responde 422 antes de llegar al service.
    """

    campos_no_nulos: ClassVar[tuple[str, ...]] = ()

    @model_validator(mode="before")
    @classmethod
    def _rechazar_nulos_explicitos(cls, data: Any) -> Any:
        """Rechaza los `null` explícitos en los campos no nulos."""
        if isinstance(data, dict):
            for campo in cls.campos_no_nulos:
                if campo in data and data[campo] is None:
                    raise ValueError(f"El campo '{campo}' no puede ser nulo")
        return data
