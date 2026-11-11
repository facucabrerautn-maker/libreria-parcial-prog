# 05 — Reglas de negocio

Reglas codificadas por dominio, con códigos tipo RN-XX y el garante esperado (base de datos o aplicación).

| Regla | Enunciado | Garante esperado |
|-------|-----------|------------------|
| RN-01 | El ISBN de un libro es único. | UNIQUE en la base; 409 |
| RN-02 | El email de un cliente es único. | UNIQUE en la base; 409 |
| RN-03 | El precio de un libro es mayor que cero y el stock nunca es negativo. | CHECK en la base y validación del DTO |
| RN-04 | Una venta se crea con sus renglones: los datos de cada renglón viajan dentro del cuerpo del alta de la venta, y no existe un alta de renglones por separado. | DTO anidado; los renglones se agregan a `venta.renglones` |
| RN-05 | Una venta tiene al menos un renglón, y un mismo libro no aparece en dos renglones. | Validación del DTO; 422 |
| RN-06 | El precio de cada renglón se copia del libro al registrar la venta y no cambia aunque después cambie el precio del libro. | El servidor lo lee de la base; nunca viaja en el DTO |
| RN-07 | El total de la venta lo calcula el servidor como suma de cantidad por precio unitario. | No viaja en el DTO |
| RN-08 | Las ventas no se modifican: registran un hecho. | No hay PATCH de ventas |
| RN-09 | Un cliente tiene como máximo un perfil. | UNIQUE en `perfil_cliente.cliente_id`; 409 |
| RN-10 | Todo listado se pagina con `limit` (de 1 a 100, por defecto 20) y `offset` (desde 0). | Restricciones en Query; 422 |
| RN-11 | El listado de libros se puede filtrar por parte del título, sin distinguir mayúsculas. | Parámetro ligado, nunca SQL armado con texto |
| RN-12 | Ningún error devuelve al cliente texto interno de la base (nombres de tablas, restricciones o trazas). | Traducción del `IntegrityError` a un mensaje propio |
