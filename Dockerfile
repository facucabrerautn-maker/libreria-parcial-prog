FROM python:3.12-alpine

# Logs sin buffer para que docker logs muestre el aviso del comprobante (D-07)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Capa de dependencias: se instala antes de copiar el código para aprovechar la caché
COPY requirements.txt .
RUN pip install --no-cache-dir --no-compile -r requirements.txt

# Copia el código de la aplicación
COPY . .

# Usuario sin privilegios para ejecutar la aplicación
RUN adduser -D -u 65532 appuser
USER appuser

# HEALTHCHECK usando wget (curl no está disponible en Alpine)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8000/health/ready || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
