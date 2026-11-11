# CHANGES — Secuencia de Implementación

> Índice canónico de todos los changes del proyecto **Librería (Parcial Programación III)**.
> Cada change es atómico: un agente puede implementarlo en una sesión (~4-6 horas).
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**

---

## Cómo usar este documento

1. Identificar el change a implementar (verificar que sus dependencias están cumplidas).
2. Leer los docs de la knowledge-base indicados en "Leer antes".
3. Ejecutar `/opsx:propose <nombre-del-change>`.
4. Al terminar el change, archivarlo con `/opsx:archive <nombre-del-change>`.
5. Marcar el checkbox `[x]` en este archivo.

---

## Árbol de dependencias

```
C-01 foundation-setup
  └── C-02 core-models
        ├── C-03 health-checks
        ├── C-04 editoriales-crud
        ├── C-05 generos-crud
        ├── C-06 autores-crud
        ├── C-08 clientes-y-perfiles
        │
        └── (C-04 + C-05 + C-06) ── C-07 libros-con-autores ── C-09 ventas-con-renglones ──┐
                                                                                              ├── C-10 tests-e2e-http
                                                                                              └── C-11 docker-despliegue
```

### Paralelismo por fase

> Cada "gate" es un punto de sincronización. Los changes dentro de un grupo pueden ejecutarse en paralelo.

```
GATE 0: ninguna
  → C-01 foundation-setup            [Agente A]

GATE 1: C-01 ✓
  → C-02 core-models                 [Agente A]

GATE 2: C-02 ✓                     ← PRIMER FORK (5 paralelos)
  → C-03 health-checks               [Agente A]
  → C-04 editoriales-crud            [Agente B]
  → C-05 generos-crud                [Agente C]
  → C-06 autores-crud                [Agente B]
  → C-08 clientes-y-perfiles         [Agente C]

GATE 3: C-04 + C-05 + C-06 ✓
  → C-07 libros-con-autores          [Agente A]

GATE 4: C-07 + C-08 ✓
  → C-09 ventas-con-renglones        [Agente A]

GATE 5: C-09 ✓
  → C-10 tests-e2e-http              [Agente C]
  → C-11 docker-despliegue           [Agente B]
```

### Camino crítico (6 changes — mínimo irreducible)

```
C-01 → C-02 → C-04 → C-07 → C-09 → C-11
```

Nota: C-05 y C-06 corren en paralelo con C-04 bajo C-02; C-07 espera a los tres. C-08 es la otra rama previa a C-09.

### Plan óptimo con 3 agentes

Este proyecto es una API pura (sin frontend), así que Agente C cubre clientes/ventas/operaciones en lugar de frontend.

```
Paso │ Agente A (Backend Core)     │ Agente B (Backend Aux - Catálogo) │ Agente C (Backend Aux - Clientes/Ventas/Ops)
─────┼─────────────────────────────┼───────────────────────────────────┼─────────────────────────────────────────────
  1  │ C-01 foundation-setup       │ —                                 │ —
  2  │ C-02 core-models            │ —                                 │ —
  3  │ C-03 health-checks          │ C-04 editoriales-crud             │ C-05 generos-crud
  4  │ —                           │ C-06 autores-crud                   │ C-08 clientes-y-perfiles
  5  │ C-07 libros-con-autores     │ —                                 │ —
  6  │ C-09 ventas-con-renglones   │ —                                 │ —
  7  │ —                           │ —                                 │ C-10 tests-e2e-http
  8  │ —                           │ C-11 docker-despliegue            │ —
```

---

## FASE 0 — Cimientos e Infraestructura

> Nota: C-01 y C-02 son secuenciales; desde C-02 en adelante se abren ramas paralelas.

### [C-01] `foundation-setup`
- **Estado**: `[x]` completado
- **Scope**: Scaffolding completo del proyecto y encima de despliegue
  - Estructura de directorios obligatoria: `app/main.py`, `app/core/{config.py,database.py}`, `app/modules/{health,editoriales,generos,autores,libros,clientes,ventas}/{models,schemas,service,router}.py`, `test/` (archivos `.http`), `Dockerfile`, `.dockerignore`, `.env.example`, `DEPLOY.md`, `README.md`
  - `app/main.py`: aplicación FastAPI, lifespan (crea motor y fábrica de sesiones en `app.state`, ejecuta `create_all` al arrancar, cierra el motor al apagar), registro de routers
  - `app/core/config.py`: lectura de `DATABASE_URL` y `SQL_ECHO` desde entorno con `python-dotenv`
  - `app/core/database.py`: motor async con `asyncpg`, fábrica `AsyncSession`, dependencia `get_session`
  - `Dockerfile`: base `python:3.12-alpine`, `pip install --no-cache-dir` antes de copiar el código, usuario no root, `HEALTHCHECK` sobre `GET /health/ready` con `wget`
  - `.dockerignore`: excluye `.env`, `.venv`, `.git`, `__pycache__`
- **Dependencias**: ninguna
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` (alcance y fuera de alcance)
  - `knowledge-base/02_descripcion_general.md` §Stack tecnológico, §Arquitectura general
  - `knowledge-base/08_arquitectura_propuesta.md` §Estructura de directorios, §Despliegue

### [C-02] `core-models`
- **Estado**: `[x]` completado
- **Scope**: Capa de persistencia base compartida por todos los módulos
  - Clase base SQLModel con metadata compartida y `SQLModel.metadata.create_all` al arrancar (sin migraciones, D-04)
  - Motor async y fábrica de sesiones reutilizable; dependencia `get_session` para inyección en routers/services
  - Convención de carga anticipada: `joinedload` para relaciones a uno, `selectinload` para colecciones (evita N+1)
  - Restricciones base: `UNIQUE`, `CHECK`, `FK` con índices en cada clave foránea
- **Dependencias**: C-01
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Entidades y restricciones, §Relaciones, §ERD
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones, §Ciclo de vida con lifespan
  - `knowledge-base/09_decisiones_y_supuestos.md` (D-04, D-05)

---

## FASE 1 — Catálogo (editoriales, géneros, autores, libros)

> Los cambios C-03, C-04, C-05, C-06 y C-08 se desbloquean juntos al terminar C-02 y pueden ir en paralelo.

### [C-03] `health-checks`
- **Estado**: `[x]` completado
- **Scope**: Endpoints de salud del módulo `health`
  - `GET /health/live` → `{"estado": "vivo"}` sin tocar la base (200)
  - `GET /health/ready` → ejecuta `SELECT 1` contra PostgreSQL; 200 si responde, 503 si no
  - Registro del router de `health` en `app/main.py`
- **Dependencias**: C-01, C-02
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` Épica 4 — Salud de la aplicación (HLT-01, HLT-02)
  - `knowledge-base/07_flujos_principales.md` §Flujo 6 — Salud
  - `knowledge-base/08_arquitectura_propuesta.md` §Despliegue (HEALTHCHECK)

### [C-04] `editoriales-crud`
- **Estado**: `[x]` completado
- **Scope**: CRUD de editoriales
  - Modelo `Editorial` (`id`, `nombre` UNIQUE, `pais`)
  - `POST /editoriales/` (201; 409 si `nombre` duplica), `GET /editoriales/` paginado con `limit`/`offset`, `GET /editoriales/{id}` (200, 404), `PATCH /editoriales/{id}` (`exclude_unset`; 200, 404, 409, 422), `GET /editoriales/{id}/libros`
  - Traducción de `IntegrityError` (UNIQUE nombre) a 409 con mensaje propio (RN-12)
  - Tests `.http`: alta, listado, detalle, duplicado 409, patch parcial
- **Dependencias**: C-02
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §tabla editorial
  - `knowledge-base/06_funcionalidades.md` Épica 1 — Catálogo (CAT-01 a CAT-04)
  - `knowledge-base/05_reglas_de_negocio.md` (RN-01, RN-10, RN-12)

### [C-05] `generos-crud`
- **Estado**: `[x]` completado
- **Scope**: CRUD de géneros
  - Modelo `Genero` (`id`, `nombre` UNIQUE)
  - `POST /generos/` (201; 409 si `nombre` duplica), `GET /generos/` paginado, `GET /generos/{id}` (200, 404), `GET /generos/{id}/libros`
  - Traducción UNIQUE nombre → 409 con mensaje propio
- **Dependencias**: C-02
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §tabla genero
  - `knowledge-base/06_funcionalidades.md` Épica 1 — Catálogo (CAT-05)
  - `knowledge-base/05_reglas_de_negocio.md` (RN-10, RN-12)

### [C-06] `autores-crud`
- **Estado**: `[x]` completado
- **Scope**: CRUD de autores
  - Modelo `Autor` (`id`, `nombre`, `nacionalidad`)
  - `GET, POST, PATCH /autores/` y `/autores/{id}` (201/200/404/409/422, `exclude_unset` en PATCH)
  - `GET /autores/{id}/libros` devolviendo libros con `rol` y `orden` de cada autoría
- **Dependencias**: C-02
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §tabla autor
  - `knowledge-base/06_funcionalidades.md` Épica 1 — Catálogo (CAT-06, CAT-07)
  - `knowledge-base/05_reglas_de_negocio.md` (RN-10)

### [C-07] `libros-con-autores`
- **Estado**: `[x]` completado
- **Scope**: Libros con asociación muchos-a-muchos con datos (autores)
  - Modelo `Libro` (`isbn` UNIQUE, `precio` NUMERIC(10,2) CHECK > 0, `stock` CHECK >= 0, `editorial_id` FK, `genero_id` FK nulo permitido) y `LibroAutor` (PK `libro_id`+`autor_id`, `orden` CHECK >= 1, `rol` CHECK en (autor, coautor, traductor, ilustrador))
  - `POST /libros/` con lista de autores anidados (201; 409 si alguna FK es inválida, sin consulta previa de existencia)
  - `GET /libros/{id}` con `joinedload` (editorial, género) y `selectinload` (autorias) — una consulta fija, sin N+1
  - `GET /libros/` con filtro `titulo` via `ILIKE %:titulo%` (parámetro ligado) + paginación `limit`/`offset`
  - `PATCH /libros/{id}` con `exclude_unset`
- **Dependencias**: C-04, C-05, C-06
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §tablas libro y libro_autor; §Relaciones
  - `knowledge-base/06_funcionalidades.md` Épica 1 — Catálogo (CAT-08, CAT-09, CAT-10)
  - `knowledge-base/07_flujos_principales.md` §Flujo 1, §Flujo 3, §Flujo 5

---

## FASE 2 — Clientes, Perfiles y Ventas

### [C-08] `clientes-y-perfiles`
- **Estado**: `[ ]` pendiente
- **Scope**: Clientes y perfil uno a uno
  - Modelo `Cliente` (`id`, `nombre`, `email` UNIQUE) y `PerfilCliente` (`id`, `cliente_id` UNIQUE FK, `telefono`, `direccion`)
  - `POST /clientes/` (201; 409 si `email` duplica), `GET /clientes/{id}` con perfil, `PATCH /clientes/{id}` (`exclude_unset`), `POST /clientes/{id}/perfil` (201; 409 si ya tiene perfil), `GET /clientes/{id}/ventas`
  - `cliente.perfil` devuelve un objeto, no una lista (D-08, RN-09)
- **Dependencias**: C-02
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §tablas cliente y perfil_cliente; §Relaciones (uno a uno)
  - `knowledge-base/06_funcionalidades.md` Épica 2 — Clientes y perfiles (CLI-01 a CLI-04)
  - `knowledge-base/05_reglas_de_negocio.md` (RN-02, RN-09, RN-12)

### [C-09] `ventas-con-renglones`
- **Estado**: `[ ]` pendiente
- **Scope**: Alta de venta con renglones anidados (flujo transaccional más crítico)
  - Modelo `Venta` (`id`, `cliente_id` FK, `fecha` con zona horaria, `total` NUMERIC(12,2) CHECK >= 0) y `RenglonVenta` (`id`, `venta_id` FK, `libro_id` FK, `cantidad` CHECK > 0, `precio_unitario` NUMERIC(10,2) CHECK > 0)
  - `POST /ventas/` con `cliente_id` + lista de `renglones` (`libro_id`, `cantidad`); al menos un renglón y libro no repetido (422); `precio_unitario` copiado del libro en el service (no viaja en el DTO, RN-06); `total` = suma cantidad × precio_unitario calculado por el servidor (no viaja en el DTO, RN-07); composición `venta → renglones`
  - `GET /ventas/` paginado (librero, todas las ventas); `GET /ventas/{id}` con `joinedload` cliente + `selectinload` renglones (sin N+1)
  - Sin `PATCH` de ventas (RN-08: las ventas no se modifican, registran un hecho)
  - `BackgroundTasks` para aviso de comprobante tras enviar la respuesta (`asyncio.sleep(0.5)` + log, D-11)
  - Traducción de FK inválida a 409 con mensaje propio
- **Dependencias**: C-07, C-08
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §tablas venta y renglon_venta; §Relaciones (composición)
  - `knowledge-base/06_funcionalidades.md` Épica 3 — Ventas (VEN-01 a VEN-07)
  - `knowledge-base/07_flujos_principales.md` §Flujo 2, §Flujo 4
  - `knowledge-base/05_reglas_de_negocio.md` (RN-04 a RN-09, RN-12)
  - `knowledge-base/08_arquitectura_propuesta.md` §BackgroundTasks

---

## FASE 3 — Pruebas, Despliegue y Operación

### [C-10] `tests-e2e-http`
- **Estado**: `[ ]` pendiente
- **Scope**: Casos de prueba en archivos `.http` bajo `test/`
  - Cobertura de todos los endpoints: health, editoriales, generos, autores, libros, clientes, ventas
  - Códigos HTTP: 201 al crear, 404, 409 (email/nombre duplicado, FK inválida, perfil ya existente), 422 (validación de DTO, venta sin renglones, libro repetido en venta)
  - Paginación `limit` (1 a 100, default 20) y `offset`; búsqueda `titulo` con `ILIKE` sin distinguir mayúsculas
  - `PATCH` con `exclude_unset` (solo campos enviados)
  - Verificación de sin N+1: detalle de libro y detalle de venta en una consulta fija
- **Dependencias**: C-09
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` (criterios de aceptación por historia de usuario)
  - `knowledge-base/07_flujos_principales.md` (número fijo de consultas por flujo)
  - `knowledge-base/09_decisiones_y_supuestos.md` (S-06: casos de prueba son archivos `.http`)

### [C-11] `docker-despliegue`
- **Estado**: `[ ]` pendiente
- **Scope**: Imagen Docker y despliegue en VPS
  - `Dockerfile` final: `python:3.12-alpine`, dependencias instaladas con `--no-cache-dir` antes de copiar el código (capa de caché), usuario no root, `docker run -d --name libreria -p <puerto>:8000 --restart unless-stopped --env-file`
  - `.env.example` con la forma de `DATABASE_URL` (sin valores reales) y `SQL_ECHO`
  - `DEPLOY.md` con instrucciones de despliegue en VPS contra PostgreSQL ya existente; nota de que `localhost` no sirve dentro del contenedor (usar `host.docker.internal` con `--add-host` o la dirección de la cátedra)
  - Ningún secreto en la imagen ni en el repositorio; `.env` no se versiona
- **Dependencias**: C-09
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/02_descripcion_general.md` §Integraciones externas (Docker)
  - `knowledge-base/08_arquitectura_propuesta.md` §Seguridad, §Variables de entorno, §Despliegue
  - `knowledge-base/09_decisiones_y_supuestos.md` (D-03, D-09, S-04, S-05)

---

## Checklist de validación al cerrar

Antes de dar por terminado este documento, verificá:

- [ ] El header dice "CHANGES — Secuencia de Implementación".
- [ ] La sección "Cómo usar este documento" tiene los 5 pasos numerados.
- [ ] El "Árbol de dependencias" usa ASCII art con `└──` y `│`.
- [ ] Hay al menos un GATE por cada fork de paralelismo detectado (GATE 2 es el PRIMER FORK con 5 cambios paralelos).
- [ ] El camino crítico tiene una flecha lineal sin ramas (6 changes).
- [ ] La tabla de "Plan óptimo con 3 agentes" tiene 3 columnas y los pasos enumerados.
- [ ] Cada change tiene exactamente 5 campos: Estado, Scope, Dependencias, Governance, Leer antes.
- [ ] Cada "Leer antes" tiene 3 a 5 archivos KB con sección cuando aplica.
- [ ] El Scope tiene bullets operacionales (modelos, endpoints, restricciones, tests).
- [ ] Cada Governance tiene uno de los 4 niveles: BAJO, MEDIO, ALTO, CRITICO.
- [ ] Los cambios están agrupados en FASES con nombres semánticos.

**Resumen**: 11 changes organizados en 4 fases. Camino crítico: C-01 → C-02 → C-04 → C-07 → C-09 → C-11 (6 changes). Gates de paralelismo: 5. Primer change recomendado: `C-01` (`foundation-setup`).

Para arrancar: `/opsx:propose C-01-foundation-setup`
