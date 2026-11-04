# ==============================================================================
# Stage 1: Builder (instalación de dependencias de producción en .venv)
# ==============================================================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Instalamos uv para resolver dependencias desde uv.lock de forma determinística
RUN pip install --no-cache-dir uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copiamos la definición de dependencias fijadas
COPY pyproject.toml uv.lock ./

# Creamos el virtualenv con dependencias de producción (sin herramientas de dev/test)
RUN uv sync --frozen --no-dev --no-install-project

# ==============================================================================
# Stage 2: Runtime (imagen final mínima sin compiladores ni dependencias dev)
# ==============================================================================
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Crear usuario y grupo no-root para ejecución segura (least privilege)
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/sh -m appuser

# Copiar el entorno virtual generado en el builder y el código fuente de app/
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --chown=appuser:appgroup app/ ./app/

# Cambiar al usuario no privilegiado
USER appuser

EXPOSE 8000

# Healthcheck interno contra el endpoint /health usando la biblioteca estándar de Python
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Ejecución de FastAPI mediante Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
