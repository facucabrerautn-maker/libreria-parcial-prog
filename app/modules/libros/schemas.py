from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import AliasChoices
from pydantic import Field as PydanticField
from sqlmodel import SQLModel

from app.modules.autores.schemas import AutorRead
from app.modules.editoriales.schemas import EditorialRead
from app.modules.generos.schemas import GeneroRead

RolAutor = Literal["autor", "coautor", "traductor", "ilustrador"]


class AutorIA(SQLModel):
    """DTO de entrada para una autoría en la creación de un libro."""

    autor_id: int
    rol: RolAutor
    orden: int = PydanticField(ge=1)


class LibroCreate(SQLModel):
    """DTO de entrada para crear un libro. Incluye la lista de autores."""

    isbn: str
    titulo: str
    precio: Decimal = PydanticField(gt=0)
    stock: int = PydanticField(default=0, ge=0)
    editorial_id: Optional[int] = None
    genero_id: Optional[int] = None
    # La consigna usa "autores"; se acepta "autorias" por compatibilidad.
    autores: List[AutorIA] = PydanticField(
        default_factory=list,
        validation_alias=AliasChoices("autores", "autorias"),
    )


class LibroUpdate(SQLModel):
    """DTO de entrada para actualizar un libro. Campos opcionales (PATCH parcial)."""

    isbn: Optional[str] = PydanticField(default=None)
    titulo: Optional[str] = PydanticField(default=None)
    precio: Optional[Decimal] = PydanticField(default=None, gt=0)
    stock: Optional[int] = PydanticField(default=None, ge=0)
    editorial_id: Optional[int] = PydanticField(default=None)
    genero_id: Optional[int] = PydanticField(default=None)
    autores: Optional[List[AutorIA]] = PydanticField(
        default=None,
        validation_alias=AliasChoices("autores", "autorias"),
    )


class AutorIARead(SQLModel):
    """DTO de salida de una autoría (con rol, orden y datos del autor)."""

    libro_id: int
    autor_id: int
    rol: str
    orden: int
    autor: Optional[AutorRead] = None

    model_config = {"from_attributes": True}


class LibroRead(SQLModel):
    """DTO de salida de un libro (con editorial, género y autores)."""

    id: int
    isbn: str
    titulo: str
    precio: Decimal
    stock: int
    editorial_id: Optional[int] = None
    genero_id: Optional[int] = None
    editorial: Optional[EditorialRead] = None
    genero: Optional[GeneroRead] = None
    autorias: List[AutorIARead] = PydanticField(default_factory=list)

    model_config = {"from_attributes": True}


class LibroResumenRead(SQLModel):
    """DTO de salida reducido para listados por editorial o género."""

    id: int
    isbn: str
    titulo: str
    precio: Decimal
    stock: int
    editorial_id: Optional[int] = None
    genero_id: Optional[int] = None

    model_config = {"from_attributes": True}


class LibroDeAutorRead(SQLModel):
    """DTO de salida de un libro visto desde un autor (rol y orden)."""

    id: int
    isbn: str
    titulo: str
    precio: Decimal
    stock: int
    rol: str
    orden: int

    model_config = {"from_attributes": True}
