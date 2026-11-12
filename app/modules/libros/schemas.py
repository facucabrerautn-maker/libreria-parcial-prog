from typing import List, Optional

from sqlmodel import SQLModel
from pydantic import Field as PydanticField


class AutorIA(SQLModel):
    """DTO de entrada para una autoría en la creación de un libro."""
    autor_id: int
    rol: str
    orden: int


class LibroCreate(SQLModel):
    """DTO de entrada para crear un libro. Incluye lista de autorías anidadas."""
    isbn: str
    titulo: str
    precio: float
    stock: int = 0
    editorial_id: Optional[int] = None
    genero_id: Optional[int] = None
    autorias: List[AutorIA] = []


class LibroUpdate(SQLModel):
    """DTO de entrada para actualizar un libro. Campos opcionales (PATCH parcial)."""
    isbn: Optional[str] = PydanticField(default=None)
    titulo: Optional[str] = PydanticField(default=None)
    precio: Optional[float] = PydanticField(default=None)
    stock: Optional[int] = PydanticField(default=None)
    editorial_id: Optional[int] = PydanticField(default=None)
    genero_id: Optional[int] = PydanticField(default=None)
    autorias: Optional[List[AutorIA]] = PydanticField(default=None)


class AutorIARead(SQLModel):
    """DTO de salida de una autoría (con rol y orden)."""
    libro_id: int
    autor_id: int
    rol: str
    orden: int

    model_config = {"from_attributes": True}


class LibroRead(SQLModel):
    """DTO de salida de un libro (incluye editorial, género y autorías)."""
    id: int
    isbn: str
    titulo: str
    precio: float
    stock: int
    editorial_id: Optional[int] = None
    genero_id: Optional[int] = None
    autorias: List[AutorIARead] = []

    model_config = {"from_attributes": True}
