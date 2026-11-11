# 06 — Funcionalidades

Historias de usuario y features organizadas por épica, basadas en los módulos mínimos obligatorios de la consigna.

## Épica 1 — Catálogo (editoriales, géneros, autores, libros)

| ID | Historia de usuario | Criterios de aceptación |
|----|---------------------|------------------------|
| CAT-01 | Como librero, quiero dar de alta una editorial para poder asociar libros a ella. | POST `/editoriales/` devuelve 201; ISBN/nombre único respeta UNIQUE; 409 si se duplica. |
| CAT-02 | Como librero, quiero listar editoriales con paginación. | GET `/editoriales/` con `limit` y `offset`; devuelve lista paginada. |
| CAT-03 | Como librero, quiero ver el detalle de una editorial y sus libros. | GET `/editoriales/{id}` devuelve EditorialRead; GET `/editoriales/{id}/libros` devuelve libros de esa editorial. |
| CAT-04 | Como librero, quiero actualizar una editorial. | PATCH `/editoriales/{id}` aplica solo campos enviados (`exclude_unset`); 200, 404, 409, 422. |
| CAT-05 | Como librero, quiero dar de alta un género para clasificar libros. | POST `/generos/` devuelve 201; nombre UNIQUE. |
| CAT-06 | Como librero, quiero dar de alta un autor con su nacionalidad. | POST `/autores/` devuelve 201. |
| CAT-07 | Como librero, quiero ver libros de un autor con rol y orden. | GET `/autores/{id}/libros` devuelve libros con rol y orden de cada autoría. |
| CAT-08 | Como librero, quiero dar de alta un libro con editorial, género opcional y autores con rol/orden. | POST `/libros/` con `editorial_id`, `genero_id` (opcional), lista `autores` (autor_id + rol + orden); 201, 409 si FK inválida. |
| CAT-09 | Como cliente, quiero buscar libros por parte del título (sin distinguir mayúsculas). | GET `/libros/` con `titulo` filtra con `ILIKE` / parámetro ligado; 422 si parámetros inválidos. |
| CAT-10 | Como cliente, quiero ver el detalle de un libro con editorial, género y autores. | GET `/libros/{id}` devuelve libro con carga anticipada de relaciones; 200, 404. |

## Épica 2 — Clientes y perfiles

| ID | Historia de usuario | Criterios de aceptación |
|----|---------------------|------------------------|
| CLI-01 | Como cliente, quiero registrarme con nombre y email. | POST `/clientes/` devuelve 201; email UNIQUE; 409 si se duplica. |
| CLI-02 | Como cliente, quiero cargar mi perfil con teléfono y dirección. | POST `/clientes/{id}/perfil` devuelve 201; `cliente_id` UNIQUE; 409 si ya tiene perfil. |
| CLI-03 | Como cliente, quiero ver mi perfil y mis ventas. | GET `/clientes/{id}` devuelve cliente con perfil; GET `/clientes/{id}/ventas` devuelve ventas del cliente. |
| CLI-04 | Como cliente, quiero actualizar mis datos. | PATCH `/clientes/{id}` aplica solo campos enviados; 200, 404, 409, 422. |

## Épica 3 — Ventas

| ID | Historia de usuario | Criterios de aceptación |
|----|---------------------|------------------------|
| VEN-01 | Como cliente, quiero registrar una venta con renglones (libro, cantidad). | POST `/ventas/` con `cliente_id` y lista `renglones`; 201 con precios copiados y total calculado. |
| VEN-02 | Como sistema, quiero que el precio de cada renglón se copie del libro al registrar la venta. | `precio_unitario` se lee de la base; no viaja en el DTO de entrada. |
| VEN-03 | Como sistema, quiero que el total de la venta se calcule como suma de cantidad × precio unitario. | `total` calculado por servidor; no viaja en el DTO. |
| VEN-04 | Como sistema, quiero que una venta tenga al menos un renglón y un libro no se repita. | Validación del DTO; 422 si no cumple. |
| VEN-05 | Como cliente, quiero ver el detalle de una venta con cliente y renglones. | GET `/ventas/{id}` devuelve venta con carga anticipada; 200, 404. |
| VEN-06 | Como librero, quiero listar todas las ventas con paginación. | GET `/ventas/` con `limit` y `offset`. |
| VEN-07 | Como sistema, quiero que las ventas no se modifiquen tras crearse. | No existe PATCH de ventas (RN-08). |

## Épica 4 — Salud de la aplicación

| ID | Historia de usuario | Criterios de aceptación |
|----|---------------------|------------------------|
| HLT-01 | Como operador, quiero saber si la aplicación está viva. | GET `/health/live` devuelve `{"estado": "vivo"}` sin tocar la base; 200. |
| HLT-02 | Como operador, quiero saber si la base de datos responde. | GET `/health/ready` ejecuta `SELECT 1`; 200 si responde. |
