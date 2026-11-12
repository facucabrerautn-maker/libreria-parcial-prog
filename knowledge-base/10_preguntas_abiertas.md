# 10 — Preguntas abiertas

Inconsistencias detectadas y preguntas abiertas priorizadas.

## Preguntas abiertas (prioridad alta)

| # | Pregunta | Por qué importa | Prioridad |
|---|----------|-----------------|-----------|
| PA-01 | ¿Se entregará un TP base previo del grupo sobre el cual construir el parcial, o se parte de cero? | Afecta qué código ya existe y qué hay que escribir desde cero. | Alta |
| PA-02 | ¿Qué dirección exacta usará `DATABASE_URL` en el VPS (host.docker.internal o otra que entregue la cátedra)? | Dentro del contenedor, `localhost` no alcanza al servidor; hay que configurar `--add-host` o usar la dirección correcta. | Alta |
| PA-03 | ¿Existe un script de datos semilla definido, o cada grupo crea el suyo? | Resuelta en el proyecto: `scripts/seed.py` (`python -m scripts.seed` / `docker exec libreria python -m scripts.seed`) deja un estado inicial conocido e idempotente. | Baja |
| PA-04 | ¿Se requiere `env.example` con campos específicos más allá de `DATABASE_URL` y `SQL_ECHO`? | La consigna menciona `env.example` con la forma de `DATABASE_URL` pero no enumera todas las variables. | Media |

## Inconsistencias detectadas

| # | Descripción | Impacto |
|---|-------------|---------|
| INC-01 | La consigna dice que no se evalúan autenticación ni autorización, pero `03_actores_y_roles.md` define una tabla RBAC con permisos por actor. | La tabla RBAC es descriptiva, no implementable; no hay JWT ni roles en el código. Se marca como documentación, no como requisito implementable. |
| INC-02 | `python:3.12-alpine` usa musl en lugar de glibc, lo que suele traer problemas con paquetes que se compilan al instalarse. | Se verificó que asyncpg, pydantic-core y el resto de `requirements.txt` se instalan sin compilar en Alpine, por lo que no hace falta instalar compilador. Riesgo residual si se agrega una dependencia que requiera compilación. |

## Preguntas abiertas (prioridad media/baja)

| # | Pregunta | Por qué importa | Prioridad |
|---|----------|-----------------|-----------|
| PB-01 | ¿Se agregarán módulos opcionales después del parcial (pagos, reportes, etc.)? | Define si la KB debe dejar hooks para extensión o quedarse fiel a la consigna. | Baja |
| PB-02 | ¿Se usará Alembic para migraciones en una versión posterior al parcial? | Afecta si documentamos `create_all` como permanente o transitorio. | Baja |
