# 03 — Actores y roles

## Actores del sistema

| Actor | Descripción |
|-------|-------------|
| Cliente | Persona que se registra, carga su perfil y realiza compras. |
| Librero | Administra el catálogo (editoriales, géneros, autores, libros) y consulta ventas. |
| Sistema | Procesa solicitudes API, aplica reglas de negocio, calcula totales, copia precios, envía aviso de comprobante. |

## Tabla RBAC y permisos

> **Nota:** La consigna del parcial no evalúa autenticación ni autorización (capítulo 5). No hay roles de usuario ni JWT en el alcance actual. Todos los endpoints son públicos desde el punto de vista de RBAC; la separación de responsabilidades es por módulo funcional, no por rol de actor.

| Recurso | Cliente | Librero | Sistema |
|---------|---------|---------|---------|
| `/health/live` | LEER | LEER | LEER |
| `/health/ready` | LEER | LEER | LEER |
| `/editoriales/*` | — | CRUD | — |
| `/generos/*` | — | CRUD | — |
| `/autores/*` | — | CRUD | — |
| `/libros/*` | LEER (listado, detalle, búsqueda) | CRUD | — |
| `/clientes/*` | CRUD propio (perfil, ventas) | — | — |
| `/ventas/*` | CREAR propia, LEER propias | LEER todas | — |

## Rutas públicas

Todas las rutas definidas en los endpoints de referencia son accesibles sin autenticación en este parcial:

- `GET /health/live`
- `GET /health/ready`
- `GET, POST /editoriales/`
- `GET /editoriales/{id}`
- `PATCH /editoriales/{id}`
- `GET /editoriales/{id}/libros`
- `GET, POST /generos/`
- `GET /generos/{id}`
- `GET /generos/{id}/libros`
- `GET, POST, PATCH /autores/`, `/autores/{id}`
- `GET /autores/{id}/libros`
- `GET, POST /libros/`
- `GET /libros/{id}`
- `PATCH /libros/{id}`
- `GET, POST /clientes/`
- `GET /clientes/{id}`
- `PATCH /clientes/{id}`
- `POST /clientes/{id}/perfil`
- `GET /clientes/{id}/ventas`
- `GET, POST /ventas/`
- `GET /ventas/{id}`
