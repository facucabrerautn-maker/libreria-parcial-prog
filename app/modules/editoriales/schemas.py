from typing import List, Optional

from pydantic import Field as PydanticField

from app.modules.editoriales.models import Editorial


class EditorialCreate(Editorial):
    """DTO de entrada para crear una editorial. No lleva id."""
    pass


class EditorialUpdate(Editorial):
    """DTO de entrada para actualizar una editorial. Campos opcionales (PATCH parcial)."""
    nombre: Optional[str] = PydanticField(default=None)
    pais: Optional[str] = PydanticField(default=None)


class EditorialRead(Editorial):
    """DTO de salida de una editorial."""
    id: int

    model_config = {"from_attributes": True}
