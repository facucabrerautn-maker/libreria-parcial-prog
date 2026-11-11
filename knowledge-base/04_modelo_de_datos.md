# 04 — Modelo de datos

## Entidades y restricciones

Los nombres de tablas y columnas son obligatorios (los casos de prueba y la corrección los usan). Se pueden agregar columnas, pero no quitar ni renombrar las indicadas.

| Tabla | Columnas | Restricciones |
|-------|----------|---------------|
| `editorial` | `id`, `nombre`, `pais` | `nombre` UNIQUE |
| `genero` | `id`, `nombre` | `nombre` UNIQUE |
| `autor` | `id`, `nombre`, `nacionalidad` | — |
| `libro` | `id`, `isbn`, `titulo`, `precio`, `stock`, `editorial_id`, `genero_id` | `isbn` UNIQUE; `precio` NUMERIC(10,2) CHECK > 0; `stock` CHECK >= 0; `genero_id` nulo permitido; FK a `editorial` y `genero` |
| `libro_autor` | `libro_id`, `autor_id`, `rol`, `orden` | PK (`libro_id`, `autor_id`); `orden` CHECK >= 1; `rol` CHECK dentro de (autor, coautor, traductor, ilustrador); FK a `libro` y `autor` |
| `cliente` | `id`, `nombre`, `email` | `email` UNIQUE |
| `perfil_cliente` | `id`, `cliente_id`, `telefono`, `direccion` | `cliente_id` UNIQUE; FK a `cliente` |
| `venta` | `id`, `cliente_id`, `fecha` (con zona horaria), `total` NUMERIC(12,2) | `total` CHECK >= 0; FK a `cliente` |
| `renglon_venta` | `id`, `venta_id`, `libro_id`, `cantidad`, `precio_unitario` NUMERIC(10,2) | `cantidad` CHECK > 0; `precio_unitario` CHECK > 0; FK a `venta` y `libro` |

## Relaciones

| Relación | Entre | Tipo | Por qué |
|----------|-------|------|---------|
| Agregación | Libro ↔ Editorial | Libro incorpora una editorial que ya existe; viaja su `id`; compartida por muchos libros. | Un libro tiene una editorial, la editorial existe independientemente. |
| Agregación opcional | Libro ↔ Género | Libro puede incorporar un género que ya existe; es optativo (nulo permitido). | Un libro puede no tener género asignado. |
| Muchos a muchos con datos | Libro ↔ Autor | Un libro tiene varios autores y un autor varios libros; el `rol` y el `orden` son de la relación. | `libro_autor` es entidad de asociación con datos propios (rol, orden). |
| Uno a uno | Cliente ↔ Perfil | Un cliente tiene como máximo un perfil. | `perfil_cliente.cliente_id` UNIQUE. |
| Asociación | Venta ↔ Cliente | La venta conoce al cliente que compró; ninguno es parte del otro. | Viaja un `cliente_id`. |
| Composición | Venta ↔ Renglón de venta | Un renglón no tiene sentido sin su venta; se crea con ella. | Los renglones viajan anidados en el alta de venta. |
| Asociación | Renglón de venta ↔ Libro | El renglón nombra un libro que ya existe. | Viaja un `libro_id`. |

## ERD (texto)

```
editorial 1 —* libro (agregación)
genero 1 —0..1 libro (agregación opcional)
libro * —* libro_autor —* autor (muchos a muchos con datos: rol, orden)
cliente 1 —0..1 perfil_cliente (uno a uno)
cliente 1 —* venta (asociación)
venta 1 —* renglon_venta (composición)
renglon_venta * —1 libro (asociación)
```

## Navegación

Cada clave foránea lleva un índice y navegación en los dos extremos con `Relationship(back_populates=...)`. La carga es siempre anticipada (joinedload para uno a uno, selectinload para colecciones) para evitar N+1.

- `libro.autorias[i].autor` — de un libro a sus autores.
- `cliente.perfil` — devuelve un objeto, no una lista.
- `venta.renglones` — colección de renglones.
- `renglon_venta.libro` — el libro del renglón.

## Seed data

La consigna no especifica datos semilla obligatorios. Se sugiere cargar datos iniciales dentro del contenedor tras el despliegue (como menciona el ejercicio 8: `docker exec libreria …` para ejecutar el comando de datos iniciales del proyecto).
