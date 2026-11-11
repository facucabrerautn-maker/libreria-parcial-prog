# .atl/skill-registry.md — Project Skill Registry

Compact rules distilled from each installed skill's SKILL.md. Used by agents to know which skills apply to this project and what conventions they enforce.

## Installed skills (4)

| # | Skill | Source | Path | When to trigger |
|---|-------|--------|------|-----------------|
| 1 | fastapi-python | Mindrally/skills | `~\.agents\skills\fastapi-python` | FastAPI / Python backend API work |
| 2 | sqlalchemy-postgres | cfircoo/claude-code-toolkit | `~\.agents\skills\sqlalchemy-postgres` | Database layer, models, migrations, queries |
| 3 | production-docker | vstorm-co/production-stack-skills | `~\.agents\skills\production-docker` | Dockerfiles, compose, containerizing, .dockerignore |
| 4 | vps-deploy | bartek-filipiuk/vps-deploy-skill | `~\.agents\skills\vps-deploy` | VPS deploy via SSH + Docker + Caddy; requires `VPS_HOST` in `.env` |

---

## 1. fastapi-python — FastAPI Python backend

**Description:** Expert in FastAPI and Python backend development; typed routes, Pydantic v2, async operations, modular routers.

**Key principles**
- Concise, technical responses with accurate Python examples
- Functional/declarative over class-based; modularize to eliminate duplication
- Descriptive variable names with auxiliary verbs (`is_active`, `has_permission`)
- Lowercase-with-underscores file/directory naming (`routers/user_routes.py`)
- RORO pattern (Receive an Object, Return an Object); export routes and utilities explicitly

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

**Description:** Multi-stage builds, non-root users, distroless images, BuildKit secrets, layer optimization, security scanning, compose best practices. Triggers on Dockerfile, docker-compose.yml, .dockerignore, or mentions of Docker/containers/images; `/production docker`.

**Multi-stage builds**
- Builder stage installs deps/compiles; runtime stage copies only final artifacts
- Never install build tools (gcc, make, git) in runtime stage; use `COPY --from=builder`

**Base image selection**
- Pin by digest (`FROM python:3.12-slim@sha256:...`) or at minimum minor version; never `latest`
- distroless ~20–50MB (max security, no shell), alpine ~7MB, slim ~150–200MB

**Non-root execution**
- Set `USER` as late as possible (after installs/copies); use `--chown` on COPY
- Verify runtime `whoami` never returns `root`; `USER 65532` for distroless

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

## 4. vps-deploy — VPS deployment via SSH + Docker + Caddy

**Description:** Deploy any Dockerized app to your own VPS via SSH, Docker, and Caddy. No middleware, no subscription. Triggers on "deploy to vps", "vps deploy", "deploy to my server", "ship to vps", "show vps apps", "vps logs", "vps env", "redeploy vps", "delete vps app", "vps status", "setup my vps". Requires `VPS_HOST` in project `.env`.

**Mandatory checkpoints (Section 0)** — all must be executed, do not skip:
1. Read `.env` and validate all variables (MANDATORY)
2. Run input validation regex checks (SECURITY — blocks command injection)
3. Verify pinned host key exists in `known_hosts` (SECURITY)
4. Check `VPS_HOST_FINGERPRINT` if set (SECURITY)
5. Verify SSH connectivity (MANDATORY)
6. Verify git remote exists (MANDATORY)
7. Check for uncommitted changes (MANDATORY)
8. Verify/create Dockerfile (MANDATORY)
9. Create `.dockerignore` if missing (MANDATORY)
10. Run framework-specific pre-deploy checks (MANDATORY)
11. STOP — Confirm deployment plan with user
12. STOP — Ask user for apps directory (first setup only)
13. STOP — Confirm VPS setup with user (skip if probe passes)
14. Run environment scan before setup (MANDATORY)
15. Run full setup script from `references/server-setup-guide.md` (MANDATORY)

**Section 1: .env validation** — Read `VPS_HOST` (required), `VPS_USER` (default root), `VPS_SSH_KEY_PATH` (default `~/.ssh/id_ed25519`), `VPS_PORT` (default 22), `VPS_APP_DOMAIN` (optional), `VPS_HOST_FINGERPRINT` (strongly recommended). Strict validation regexes block command/path injection. If `VPS_HOST` missing, stop and ask user to add VPS details to `.env`.

**Section 2: SSH command pattern** — Use pinned-host-key SSH array (not flat string) for ALL remote commands: `BatchMode=yes`, `StrictHostKeyChecking=yes`, `ConnectTimeout=10`, `-i` key, `-p` port. `set -euo pipefail` inside heredocs. Never interpolate untrusted values directly into remote command strings — pass dynamic values via `env` into quoted heredocs.

**Section 3: Prerequisites check** — SSH key exists; SSH connectivity (`echo ok`); git remote exists; uncommitted changes (warn); Dockerfile present (auto-detect stack via marker files table if missing); `.dockerignore` created if missing (commit to git); framework-specific pre-deploy checks (Next.js standalone output, Prisma migrations/DATABASE_URL, etc.).

**Section 4: Deploy Protocol** — derive and validate app name (lowercase, hyphens, 63 chars max); STOP to confirm deployment plan with user; VPS server setup (Docker, Compose plugin, network `web`, UFW firewall, `$APPS_DIR`, `/etc/vps-deploy.conf`, Caddy in Docker); create app directory; clone or update code (depth 1, branch); create `.dockerignore`; generate `docker-compose.yml` (with/without domain → host port mapping vs Caddy reverse_proxy); create/update `.env` on VPS (`PORT=`); build and start (`docker compose up -d --build --force-recreate`); configure Caddy site config (reverse_proxy + security headers); health check (wait for `healthy`, then curl); report result.

**Section 5: Management commands** — `show vps apps`, `vps logs [app]`, `set vps env KEY=VALUE`, `show vps env` (values masked), `redeploy vps [app]`, `delete vps app [app]` (confirm first, realpath boundary checks), `vps status`, `vps rollback [app]`.

**Section 6: Error handling** — table mapping errors (no VPS_HOST, no pinned host key, fingerprint mismatch, connection timeout, permission denied, host key changed, invalid app name/domain, no Dockerfile, no git remote, clone auth failure, build failure, container exits immediately, Caddy reload failure, domain not resolving, disk full, port in use) to cause and user guidance.

**Notes** — Direct SSH to VPS — no middleware/subscription/third-party services. `BatchMode=yes` always — SSH key auth required, never password prompts. Host keys pinned and verified (`StrictHostKeyChecking=yes`) before any remote command. DNS must point to VPS IP before deploying with a domain (Caddy needs this for SSL). Private repos need an SSH deploy key on the VPS or HTTPS token in the git URL. App names and key config values validated with strict allowlists before command execution. Untrusted values passed via `env` into quoted SSH heredocs (no direct string interpolation). Deletion uses realpath boundary checks to prevent accidental removal outside `$APPS_DIR`. Env vars stored on VPS at `$APPS_DIR/{name}/.env` — never committed to git. Multiple apps share Docker `web` network and Caddy reverse proxy. Each app gets its own directory at `$APPS_DIR/{name}/` with repo, compose file, and env. Apps directory path stored in `/etc/vps-deploy.conf` on VPS — set on first setup, read automatically on subsequent runs. Caddy handles SSL automatically via Let's Encrypt — no manual certificate management. `managed-by=vps-deploy` Docker label identifies apps deployed by this skill. All setup scripts idempotent — safe to re-run. Ubuntu and Debian supported.

---

## How to use this registry

- When the user's task matches a skill's triggers, load that skill and apply its rules.
- Cross-skill: this project uses FastAPI + SQLAlchemy 2.0 async + asyncpg + PostgreSQL 16 + Docker (python:3.12-alpine) — coordinate fastapi-python routes with sqlalchemy-postgres models/schemas/repositories, containerize per production-docker, and deploy to VPS per vps-deploy (requires `VPS_HOST` in `.env`).
- Source of truth for full detail: each skill's `SKILL.md` at `~\.agents\skills\<skill>\SKILL.md`.
