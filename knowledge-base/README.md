# Knowledge Base — Librería (Parcial Programación III)

Índice de la base de conocimiento del proyecto. Cada archivo cubre un aspecto del sistema API de librería para catálogo y ventas, desarrollado como parcial de Programación III (Unidades 1 a 4).

| # | Archivo | Contenido |
|---|---------|-----------|
| 01 | `01_vision_y_objetivos.md` | Propósito, objetivos por actor, alcance, fuera de alcance |
| 02 | `02_descripcion_general.md` | Stack tecnológico, arquitectura general, integraciones externas |
| 03 | `03_actores_y_roles.md` | Actores del sistema, tabla RBAC, permisos, rutas públicas |
| 04 | `04_modelo_de_datos.md` | Entidades, ERD, relaciones, seed data |
| 05 | `05_reglas_de_negocio.md` | Reglas codificadas por dominio (códigos RN-XX) |
| 06 | `06_funcionalidades.md` | Historias de usuario / features organizadas por épica |
| 07 | `07_flujos_principales.md` | Flujos extremo a extremo (alta de venta, detalle de libro, etc.) |
| 08 | `08_arquitectura_propuesta.md` | Patrones, estructura de directorios, seguridad, variables de entorno |
| 09 | `09_decisiones_y_supuestos.md` | Decisiones de diseño documentadas + supuestos inferidos |
| 10 | `10_preguntas_abiertas.md` | Inconsistencias detectadas + preguntas abiertas priorizadas |

**Stack:** Python 3.12, FastAPI 0.111, SQLModel 0.0.24, SQLAlchemy 2.0 async, asyncpg, PostgreSQL 16, python-dotenv, uvicorn, Docker (`python:3.12-alpine`).

**Dominio:** Librería de barrio — catálogo de libros (editoriales, géneros, autores) y ventas con renglones.

**Enfoque:** Fidelidad a la consigna del parcial, módulos mínimos obligatorios (`health`, `editoriales`, `generos`, `autores`, `libros`, `clientes`, `ventas`).
