# Despliegue — Librería API

## Imagen Docker

La imagen se construye con:

```bash
docker build -t libreria .
```

## Ejecución en contenedor

```bash
docker run -d --name libreria -p <puerto>:8000 --restart unless-stopped \
  --env-file .env libreria
```

- `-p <puerto>:8000` publica solo la aplicación en el puerto asignado.
- `--restart unless-stopped` hace que Docker vuelva a levantar el contenedor si termina.
- `--env-file` entrega la configuración desde un archivo que vive en el servidor, fuera del repositorio y de la imagen.

## Base de datos

La base de datos no forma parte de la imagen. El contenedor se conecta a un PostgreSQL 16 ya existente en el VPS a través de `DATABASE_URL`.

**Nota:** Dentro de un contenedor, `localhost` es el propio contenedor. Si PostgreSQL corre directamente en el servidor, el contenedor la alcanza por `host.docker.internal` (habilitar con `--add-host=host.docker.internal:host-gateway` en Linux) o la dirección que entregue la cátedra.

## HEALTHCHECK

La imagen declara un `HEALTHCHECK` sobre `GET /health/ready`. En Alpine no hay `curl`; se usa `wget` con la dirección `127.0.0.1`.

## Seguridad

- La aplicación no corre como root (usuario `appuser`, UID 65532).
- Ningún secreto dentro de la imagen: `DATABASE_URL` entra como variable de entorno.
- El `.env` no se versiona; existe `.env.example` con la forma del valor.

## Actualización

Se construye la imagen de nuevo, se elimina el contenedor y se vuelve a correr. Los datos no se pierden porque viven en la base del servidor, no en el contenedor.
