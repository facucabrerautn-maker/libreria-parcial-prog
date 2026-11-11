from typing import List, Optional

from pydantic import Field as PydanticField

from app.modules.libros.models import Libro, LibroAutor


class AutorIA(LibroAutor):
    """DTO de entrada para una autoría en la creación de un libro."""
    model_config = {"from_attributes": True}


class LibroCreate(Libro):
    """DTO de entrada para crear un libro. Incluye lista de autorías anidadas."""
    autorias: List[AutorIA] = []

    model_config = {"from_attributes": True}


class LibroUpdate(Libro):
    """DTO de entrada para actualizar un libro. Campos opcionales (PATCH parcial)."""
    isbn: Optional[str] = PydanticField(default=None)
    titulo: Optional[str] = PydanticField(default=None)
    precio: Optional[float] = PydanticField(default=None)
    stock: Optional[int] = PydanticField(default=None)
    editorial_id: Optional[int] = PydanticField(default=None)
    genero_id: Optional[int] = PydanticField(default=None)
    autorias: Optional[List[AutorIA]] = PydanticField(default=None)

    model_config = {"from_attributes": True}


class AutorIARead(LibroAutor):
    """DTO de salida de una autoría (con rol y orden)."""
    model_config = {"from_attributes": True}


class LibroRead(Libro):
    """DTO de salida de un libro (incluye editorial, género y autorías)."""
    id: int
    autorias: List[AutorIARead] = []

    model_config = {"from_attributes": True}
