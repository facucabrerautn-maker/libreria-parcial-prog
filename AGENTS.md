# Librería (Parcial Programación III) — Instrucciones para Agentes

## Stack Tecnológico

| Componente | Versión | Uso |
|------------|---------|-----|
| Python | 3.12 | Lenguaje |
| FastAPI | 0.111 | Framework web; handlers `async def` |
| SQLModel | 0.0.37 | Modelos de tabla y contratos |
| SQLAlchemy | 2.0 (async) | Motor, sesión y carga anticipada |
| asyncpg | 0.32 | Controlador asíncrono de PostgreSQL |
| PostgreSQL | 16 | Base de datos (ya existente en el VPS) |
| python-dotenv | 1.0 | Lectura del archivo `.env` |
| uvicorn | — | Servidor ASGI |
| Docker | 20.10 | Construir imagen y correr contenedor |

Imagen base: `python:3.12-alpine` (límite de 100 MB para la imagen base).

> SQLModel 0.0.24 no es compatible con Pydantic 2.14 (falla al importar con
> `Field 'id' requires a type annotation`). Por eso se fija `sqlmodel==0.0.37`,
> que mantiene la API usada por el proyecto y funciona con Pydantic 2.x.

## Base de Conocimiento

La KB vive en `knowledge-base/` con estos 11 archivos:

| # | Archivo | Contenido |
|---|---------|-----------|
| 01 | `01_vision_y_objetivos.md` | Propósito, objetivos por actor, alcance, fuera de alcance |
| 02 | `02_descripcion_general.md` | Stack tecnológico, arquitectura general, integraciones externas |
| 03 | `03_actores_y_roles.md` | Actores del sistema, tabla RBAC, permisos, rutas públicas |
| 04 | `04_modelo_de_datos.md` | Entidades, ERD, relaciones, seed data |
| 05 | `05_reglas_de_negocio.md` | Reglas codificadas por dominio (códigos RN-XX) |
| 06 | `06_funcionalidades.md` | Historias de usuario / features organizadas por épica |
| 07 | `07_flujos_principales.md` | Flujos extremo a extremo |
| 08 | `08_arquitectura_propuesta.md` | Patrones, estructura de directorios, seguridad, variables de entorno |
| 09 | `09_decisiones_y_supuestos.md` | Decisiones de diseño documentadas + supuestos inferidos |
| 10 | `10_preguntas_abiertas.md` | Inconsistencias detectadas + preguntas abiertas priorizadas |

**Dominio:** Librería de barrio — catálogo de libros (editoriales, géneros, autores) y ventas con renglones.

**Enfoque:** Fidelidad a la consigna del parcial, módulos mínimos obligatorios (`health`, `editoriales`, `generos`, `autores`, `libros`, `clientes`, `ventas`).

## Skills Disponibles

| Agente | Rol | Skills que carga |
|--------|-----|------------------|
| Backend Core | FastAPI/SQLModel/UoW | `fastapi-python`, `sqlalchemy-postgres` |
| Backend Aux | Servicios/integraciones/Docker | `production-docker` |
| Orquestación | KB / Roadmap / AGENTS.md | `kb-creator`, `roadmap-generator`, `agent-instruction` |

Los compact rules de cada skill los resuelve el orquestador desde `.atl/skill-registry.md` (generado por `skill-registry`; no versionado — no está en el repo).

Skills instaladas en `~\.agents\skills\`:
- `fastapi-python` — FastAPI/Pydantic v2 async backend: RORO pattern, `def`/`async def`, type hints, lifespan, dependency injection, guard clauses
- `sqlalchemy-postgres` — SQLAlchemy 2.0 async + asyncpg + PostgreSQL + Alembic: `Mapped[]` annotations, separación de preocupaciones (models/schemas/repositories/services), `from_attributes=True`, repo pattern
- `production-docker` — multi-stage builds, non-root `USER`, distroless/slim images, BuildKit secrets, `.dockerignore`, `HEALTHCHECK`, Trivy scanning, compose/resource/network hardening, runtime hardening

## Roadmap de Changes

El roadmap está en `CHANGES.md` (11 changes, `C-01` a `C-11`, organizados en 4 fases).

**Camino crítico:** `C-01 → C-02 → C-04 → C-07 → C-09 → C-11` (6 changes).

**Primer change recomendado:** `C-01` (`foundation-setup`) — ejecutar con `/opsx:propose C-01-foundation-setup`.

**Gates de paralelismo:** 5 gates; GATE 2 es el primer fork con 5 cambios paralelos (`C-03`, `C-04`, `C-05`, `C-06`, `C-08`).

## Reglas Duras (específicas del proyecto)

Las siguientes reglas son específicas de este proyecto. No hay un `~/.claude/CLAUDE.md` global instalado, por lo que no hay reglas universales heredadas que referenciar — todas las reglas duras viven acá.

| # | Regla |
|---|-------|
| R-01 | `snake_case` para archivos, variables, funciones, directorios. |
| R-02 | Type hints en todas las firmas de función. |
| R-03 | `def` para funciones puras, `async def` para operaciones async. Ninguna llamada bloqueante dentro de handlers (`time.sleep`, `requests`, acceso síncrono a la base). |
| R-04 | Pydantic `BaseModel` consistentemente para validación. DTO separados de modelos de tabla (Create, Update, Read). |
| R-05 | PATCH aplica solo campos enviados (`exclude_unset`). |
| R-06 | Dinero con `Decimal`, nunca `float`. |
| R-07 | Carga anticipada: `joinedload` para relaciones a uno, `selectinload` para colecciones. Nunca carga perezosa (evita N+1). |
| R-08 | `HTTPException` para errores esperados. Nunca exponer texto interno de la base (nombres de tablas, restricciones, trazas) al cliente. |
| R-09 | SQL nunca armado por concatenación de texto con datos del usuario. Usar parámetros ligados. |
| R-10 | Ninguna contraseña ni secreto en el código, el repositorio ni la imagen Docker. |
| R-11 | Restricciones de base garantizan unicidad (`UNIQUE`) e integridad (`CHECK`, `FK`). No verificar con consulta previa antes de escribir. |
| R-12 | Ventas no se modifican: no existe `PATCH` de ventas. |
| R-13 | El precio de cada renglón se copia del libro al registrar la venta; nunca viaja en el DTO de entrada. |
| R-14 | El total de la venta lo calcula el servidor (suma de cantidad × precio unitario); no viaja en el DTO. |
| R-15 | Imagen base `python:3.12-alpine`; usuario no root (`USER`); sin secretos en la imagen; `.dockerignore` excluye `.env`, `.venv`, `.git`, `__pycache__`. |
| R-16 | `DATABASE_URL` entra como variable de entorno (`--env-file`), nunca se hornea en la imagen ni se versiona. |
| R-17 | `HEALTHCHECK` sobre `GET /health/ready` (con `wget` en Alpine, dirección `127.0.0.1`, no `localhost`). |
| R-18 | `create_all` al arrancar (sin migraciones en este parcial). |

## Flujo de Trabajo

1. Leer `knowledge-base/` para entender el dominio y el stack.
2. Leer `CHANGES.md` para identificar el change a implementar y sus dependencias.
3. Ejecutar `/opsx:propose <nombre-del-change>` para comenzar un change.
4. Implementar siguiendo las Reglas Duras y los patrones de la KB.
5. Archivar el change con `/opsx:archive <nombre-del-change>` y marcar `[x]` en `CHANGES.md`.
