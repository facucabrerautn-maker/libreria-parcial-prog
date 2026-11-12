"""Script de datos iniciales (seed) del proyecto.

Deja la base en un estado inicial conocido y reproducible: borra los datos
existentes y vuelve a insertar editoriales, géneros, autores, libros y
clientes con ids conocidos (1, 2, ...).

Uso local:
    python -m scripts.seed

Uso dentro del contenedor (después de `docker run`):
    docker exec libreria python -m scripts.seed

La conexión se toma de `DATABASE_URL` (variable de entorno o archivo `.env`),
igual que la aplicación. No se crean ventas: los casos de prueba de
`test/ventas.http` las crean para dejar ids previsibles.
"""

import asyncio
import sys
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.config import DATABASE_URL
from app.modules.autores.models import Autor
from app.modules.clientes.models import Cliente, PerfilCliente
from app.modules.editoriales.models import Editorial
from app.modules.generos.models import Genero
from app.modules.libros.models import Libro, LibroAutor
from app.modules.ventas.models import RenglonVenta, Venta  # noqa: F401

# Orden de borrado: primero las tablas que dependen de otras.
TABLAS_EN_ORDEN_DE_BORRADO = (
    "renglon_venta",
    "venta",
    "perfil_cliente",
    "cliente",
    "libro_autor",
    "libro",
    "autor",
    "genero",
    "editorial",
)


async def _limpiar_base(session: AsyncSession, dialecto: str) -> None:
    """Vacía las tablas y reinicia los contadores de id."""
    tablas = ", ".join(TABLAS_EN_ORDEN_DE_BORRADO)
    if dialecto == "postgresql":
        await session.execute(
            text(f"TRUNCATE TABLE {tablas} RESTART IDENTITY CASCADE")
        )
    else:
        # SQLite y otros motores: borrar en orden de dependencia.
        # En SQLite el id vuelve a empezar en 1 cuando la tabla queda vacía,
        # así que no hace falta reiniciar ninguna secuencia.
        for tabla in TABLAS_EN_ORDEN_DE_BORRADO:
            await session.execute(text(f"DELETE FROM {tabla}"))
    await session.commit()


async def seed() -> None:
    """Carga los datos iniciales. Falla con mensaje claro si no hay URL."""
    if not DATABASE_URL:
        raise SystemExit(
            "DATABASE_URL no está definida. Configure el .env o pase la "
            "variable de entorno antes de ejecutar el seed."
        )

    engine = create_async_engine(DATABASE_URL)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    try:
        # Crea las tablas que falten (mismo criterio que el arranque de la app).
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        async with session_factory() as session:
            await _limpiar_base(session, engine.dialect.name)

            editorial_sudamericana = Editorial(
                nombre="Editorial Sudamericana", pais="Argentina"
            )
            editorial_anagrama = Editorial(nombre="Anagrama", pais="España")
            genero_novela = Genero(nombre="Novela")
            genero_cuento = Genero(nombre="Cuento")
            autor_cortazar = Autor(
                nombre="Julio Cortázar", nacionalidad="Argentina"
            )
            autor_borges = Autor(
                nombre="Jorge Luis Borges", nacionalidad="Argentina"
            )
            autor_piglia = Autor(nombre="Ricardo Piglia", nacionalidad="Argentina")

            session.add_all(
                [
                    editorial_sudamericana,
                    editorial_anagrama,
                    genero_novela,
                    genero_cuento,
                    autor_cortazar,
                    autor_borges,
                    autor_piglia,
                ]
            )
            await session.commit()

            for entidad in (
                editorial_sudamericana,
                editorial_anagrama,
                genero_novela,
                genero_cuento,
                autor_cortazar,
                autor_borges,
                autor_piglia,
            ):
                await session.refresh(entidad)

            libro_rayuela = Libro(
                isbn="978-950-00-0006-6",
                titulo="Rayuela",
                precio=Decimal("25000.00"),
                stock=4,
                editorial_id=editorial_sudamericana.id,
                genero_id=genero_novela.id,
            )
            libro_bestiario = Libro(
                isbn="978-950-00-0012-7",
                titulo="Bestiario",
                precio=Decimal("18000.00"),
                stock=3,
                editorial_id=editorial_sudamericana.id,
                genero_id=genero_cuento.id,
            )
            libro_ficciones = Libro(
                isbn="978-84-339-7000-1",
                titulo="Ficciones",
                precio=Decimal("21000.00"),
                stock=5,
                editorial_id=editorial_anagrama.id,
                genero_id=genero_cuento.id,
            )
            libro_respiracion = Libro(
                isbn="978-84-339-7001-8",
                titulo="Respiración artificial",
                precio=Decimal("27000.00"),
                stock=2,
                editorial_id=editorial_anagrama.id,
                genero_id=genero_novela.id,
            )

            session.add_all(
                [
                    libro_rayuela,
                    libro_bestiario,
                    libro_ficciones,
                    libro_respiracion,
                ]
            )
            await session.commit()

            for libro in (
                libro_rayuela,
                libro_bestiario,
                libro_ficciones,
                libro_respiracion,
            ):
                await session.refresh(libro)

            session.add_all(
                [
                    LibroAutor(
                        libro_id=libro_rayuela.id,
                        autor_id=autor_cortazar.id,
                        rol="autor",
                        orden=1,
                    ),
                    LibroAutor(
                        libro_id=libro_bestiario.id,
                        autor_id=autor_cortazar.id,
                        rol="autor",
                        orden=1,
                    ),
                    LibroAutor(
                        libro_id=libro_ficciones.id,
                        autor_id=autor_borges.id,
                        rol="autor",
                        orden=1,
                    ),
                    LibroAutor(
                        libro_id=libro_respiracion.id,
                        autor_id=autor_piglia.id,
                        rol="autor",
                        orden=1,
                    ),
                ]
            )

            cliente_ana = Cliente(nombre="Ana Gómez", email="ana@example.com")
            cliente_tomas = Cliente(
                nombre="Tomás Ríos", email="tomas@example.com"
            )
            # Orden intencional: Tomás Ríos queda con id 2, como en el
            # ejemplo de POST /ventas/ de la consigna (caso C-06 / D-03).
            session.add_all([cliente_ana, cliente_tomas])
            await session.commit()
            await session.refresh(cliente_tomas)

            session.add(
                PerfilCliente(
                    cliente_id=cliente_tomas.id,
                    telefono="+54 11 1234-5678",
                    direccion="Calle Falsa 123",
                )
            )
            await session.commit()

        print(
            "Datos iniciales cargados: 2 editoriales, 2 géneros, 3 autores, "
            "4 libros y 2 clientes."
        )
    finally:
        await engine.dispose()


def main() -> None:
    """Punto de entrada del script."""
    try:
        asyncio.run(seed())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"Error al cargar los datos iniciales: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
