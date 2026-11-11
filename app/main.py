from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import DATABASE_URL, SQL_ECHO
from app.core.database import close_db, init_db
from app.modules.autores.router import router as autores_router
from app.modules.clientes.router import router as clientes_router
from app.modules.editoriales.router import router as editoriales_router
from app.modules.generos.router import router as generos_router
from app.modules.health.router import router as health_router
from app.modules.libros.router import router as libros_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(DATABASE_URL, echo=SQL_ECHO)
    yield
    await close_db()


app = FastAPI(
    title="Librería API",
    description="API REST para catálogo y ventas de una librería de barrio",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(editoriales_router)
app.include_router(generos_router)
app.include_router(autores_router)
app.include_router(libros_router)
app.include_router(clientes_router)


@app.get("/")
async def root():
    return {"mensaje": "Librería API — en funcionamiento"}
