# ===========================================
# SembrarIA - Backend
# Multi-stage build para minimizar tamano de imagen
# ===========================================

# ---- Stage 1: builder con GDAL para rasterio ----
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# GDAL/GEOS/PROJ para rasterio + geopandas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar GDAL Python que matchee la version del sistema
RUN GDAL_VERSION=$(gdal-config --version) && \
    pip install --no-cache-dir GDAL==$GDAL_VERSION

COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Stage 2: runtime minimo ----
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/sembraria/.local/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgdal32 \
    libgeos3.13.0 \
    libproj25 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash sembraria

USER sembraria
WORKDIR /home/sembraria

# Copiar dependencias desde el builder
COPY --from=builder /root/.local /home/sembraria/.local
COPY --chown=sembraria:sembraria apps/api ./apps/api
COPY --chown=sembraria:sembraria config ./config
COPY --chown=sembraria:sembraria scripts ./scripts
COPY --chown=sembraria:sembraria data ./data

# El .env NO se copia (debe venir como secret o mount externo)
# Crear uno placeholder para que la app no falle al boot
RUN cat > .env <<'EOF'
APP_ENV=production
APP_NAME=SembrarIA
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/sembraria
JWT_SECRET=REEMPLAZAR_EN_PRODUCCION
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24
JWT_KEY_ID=v1
JWT_GRACE_SECONDS=86400
RASTER_INPUTS_DIR=/home/sembraria/data/inputs
RASTER_OUTPUTS_DIR=/home/sembraria/data/outputs
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=
LOGIN_RATE_LIMIT_PER_MINUTE=10
EOF

# Directorios con permisos de escritura
RUN mkdir -p /home/sembraria/data/outputs && \
    mkdir -p /home/sembraria/data/inputs

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/live || exit 1

CMD ["python", "-m", "uvicorn", "sembraria.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-level", "info"]
