# Dockerfile simple para el backend en desarrollo (FastAPI + uv)
# Sin multi-stage según consigna del Ticket T4
FROM python:3.12-slim

WORKDIR /app

# Instalamos uv para gestionar las dependencias de forma rápida
RUN pip install --no-cache-dir uv

# Copiamos la definición de paquetes y candado
COPY pyproject.toml uv.lock ./

# Instalamos las dependencias en el sistema del contenedor
RUN uv pip install --system -r pyproject.toml

# Copiamos el código fuente de la aplicación
COPY app/ ./app/

# Exponemos el puerto de la API
EXPOSE 8000

# Iniciamos Uvicorn en 0.0.0.0 para ser accesible desde afuera del contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
