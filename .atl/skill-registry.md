# .atl/skill-registry.md — Project Skill Registry

Compact rules distilled from each installed skill's SKILL.md. Used by agents to know which skills apply to this project and what conventions they enforce.

## Installed skills (3)

| # | Skill | Source | Path | When to trigger |
|---|-------|--------|------|-----------------|
| 1 | fastapi-python | Mindrally/skills | `~\.agents\skills\fastapi-python` | FastAPI / Python backend API work |
| 2 | sqlalchemy-postgres | cfircoo/claude-code-toolkit | `~\.agents\skills\sqlalchemy-postgres` | Database layer, models, migrations, queries |
| 3 | production-docker | vstorm-co/production-stack-skills | `~\.agents\skills\production-docker` | Dockerfiles, compose, containerizing, .dockerignore |

---

## 1. fastapi-python — FastAPI Python backend

**Description:** Expert in FastAPI and Python backend development; typed routes, Pydantic v2, async operations, modular routers.

**Key principles**
- Concise, technical responses with accurate Python examples
- Functional/declarative over class-based; modularize to eliminate duplication
- Descriptive variable names with auxiliary verbs (`is_active`, `has_permission`)
- Lowercase-with-underscores file/directory naming (`routers/user_routes.py`)
- Export routes and utilities explicitly; RORO pattern (Receive an Object, Return an Object)

**Standards**
- `def` for pure functions, `async def` for async operations
- Type hints on all function signatures; Pydantic models over raw dicts
- Structure: exported router → sub-routes → utilities → static content → types (models/schemas)
- Early returns / guard clauses for errors; happy path last; avoid unnecessary `else`
- Lifespan context managers for startup/shutdown; middleware for logging/error monitoring
- `HTTPException` for expected errors; Pydantic `BaseModel` consistently for validation

**Performance**
- Minimize blocking I/O; async for all DB and API calls
- Cache with Redis or in-memory; optimize Pydantic serialization/deserialization; lazy load large datasets

**Conventions**
- FastAPI dependency injection; prioritize API performance metrics (response time, latency, throughput); structure routes/dependencies for readability

**Dependencies:** FastAPI, Pydantic v2, asyncpg/aiomysql, SQLAlchemy 2.0

---

## 2. sqlalchemy-postgres — SQLAlchemy 2.0 + Pydantic + PostgreSQL

**Description:** Expert guidance for SQLAlchemy 2.0 + Pydantic + PostgreSQL. Automatically activated for DB tasks (setup database layer, define models, create migrations, query patterns, full implementation).

**Stack:** SQLAlchemy 2.0 async (asyncpg driver), Pydantic v2 validation/serialization, Alembic migrations, PostgreSQL only.

**Core principles**
- Separation of Concerns: `models/` (SQLAlchemy ORM), `schemas/` (Pydantic), `repositories/` (data access), `services/` (business logic)
- Type Safety First: SQLAlchemy 2.0 style with `Mapped[]` type annotations (`id: Mapped[int] = mapped_column(primary_key=True)`)
- Async by Default: `create_async_engine("postgresql+asyncpg://...")`, `AsyncSession`
- Pydantic-SQLAlchemy Bridge: keep models and schemas separate but mappable (`ConfigDict(from_attributes=True)`)
- Repository Pattern: abstract DB operations for testability

**Auto-detection triggers:** database, db, sqlalchemy, postgres, postgresql, model, migration, alembic, repository, crud, query, async session, connection pool

**File structure:** `src/db/{__init__,base,session,dependencies}`, `models/`, `schemas/`, `repositories/`, `alembic/`

**Success criteria:** async engine + session factory; base model with `id`/`created_at`/`updated_at`; `Mapped[]` annotations; Pydantic schemas with `from_attributes=True`; Alembic configured for async; repository pattern; FastAPI dependency for session injection; connection pooling for production.

---

## 3. production-docker — Docker production hardening

**Description:** Multi-stage builds, non-root users, distroless images, BuildKit secrets, layer optimization, security scanning, compose best practices. Triggers on Dockerfile, docker-compose.yml, .dockerignore, or mentions of Docker/containers/images.

**Multi-stage builds**
- Builder stage installs deps/compiles; runtime stage copies only final artifacts
- Never install build tools (gcc, make, git) in runtime stage; use `COPY --from=builder`

**Base image selection**
- Pin by digest (`FROM python:3.12-slim@sha256:...`) or at minimum minor version; never `latest`
- distroless ~20–50MB (max security, no shell), alpine ~7MB, slim ~150–200MB

**Non-root execution**
- Set `USER` as late as possible (after installs/copies); use `--chown` on COPY
- Verify runtime `whoami` never returns `root`

**BuildKit secrets**
- Never `ARG`/`ENV`/`COPY` secrets (visible in `docker history`/`docker inspect`)
- Use `RUN --mount=type=secret,id=...` and `--secret id=...,src=...` at build time

**Layer optimization**
- Copy dependency manifests (`requirements.txt`) before application code
- Install deps in a separate layer from code; combine related `RUN` with `&&`; cleanup in same layer (`rm -rf /var/lib/apt/lists/*`); `pip install --no-cache-dir --no-compile`

**.dockerignore**
- Mandatory: `.git`, `.env`, `.env.*`, `*.pyc`, `__pycache__`, `.venv`, `node_modules`, `.idea`, `.vscode`, `tests/`, `test/`, `docs/`, `*.md` (except `README.md`), `docker-compose*.yml`, `Dockerfile*`, `.dockerignore`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- Every Dockerfile project MUST have a .dockerignore; context >50MB usually means missing entries

**Health checks**
- Every production Dockerfile must have a `HEALTHCHECK` (exec form `CMD ["..."]`)
- Health endpoint must verify real functionality (DB connection, not just 200 OK); no `curl` in distroless

**Security scanning**
- Scan in CI on every build with Trivy; `--exit-code 1`, severity `HIGH,CRITICAL`, `--ignore-unfixed`; pin Trivy version; maintain `.trivyignore` with justifications

**Compose best practices**
- `depends_on` with `condition: service_healthy`; set `mem_limit`/`cpus` resource limits; `restart: unless-stopped`; named volumes for persistent data (no bind mounts in prod); `env_file` for env vars (no hardcoded secrets); pin image tags; separate dev vs prod compose files; network isolation (frontend/backend networks)

**Runtime hardening**
- `read_only: true` + `tmpfs` for writable paths; `cap_drop: ALL` (add back only needed, e.g. `NET_BIND_SERVICE`); `security_opt: no-new-privileges:true`

**Anti-patterns → fixes:** running as root → `USER 65532`; `FROM ...:latest` → pin version+digest; `COPY . .` without .dockerignore → add .dockerignore; `ARG SECRET=...` → BuildKit secrets; single-stage → multi-stage; dev deps in prod → `--only=production`; no HEALTHCHECK → add HEALTHCHECK; hardcoded ENV secrets → `env_file`; no resource limits → set `mem_limit`/`cpus`.

---

## How to use this registry

- When the user's task matches a skill's triggers, load that skill and apply its rules.
- Cross-skill: this project uses FastAPI + SQLAlchemy 2.0 async + asyncpg + PostgreSQL 16 + Docker (python:3.12-alpine) — coordinate fastapi-python routes with sqlalchemy-postgres models/schemas/repositories, and containerize per production-docker.
- Source of truth for full detail: each skill's `SKILL.md` at `~\.agents\skills\<skill>\SKILL.md`.
