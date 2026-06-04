# apps/api — Backend FastAPI

API REST para SembrarIA: análisis sincrónico de aptitud agrícola, gestión de fincas, alertas, reportes PDF y precios de mercado.

## Stack

- **FastAPI** 0.115 — HTTP framework async con OpenAPI auto
- **SQLAlchemy 2.0** + **GeoAlchemy2** — ORM con PostGIS
- **Pydantic v2** — validación y settings
- **rasterio** + **numpy** — extracción zonal sobre GeoTIFFs
- **ReportLab** — generación de PDF
- **python-jose** + **passlib[bcrypt]** — JWT + hashing

## Estructura

```
apps/api/
├── sembraria/              # Paquete Python (importable)
│   ├── main.py             # Entry: uvicorn sembraria.main:app
│   ├── config.py           # Settings + YAML loaders
│   ├── database.py         # Engine, Session, Base
│   ├── security.py         # JWT + bcrypt
│   ├── init_db.py          # Crea tablas + corre SQL en config/db/
│   ├── api/                # Routers REST
│   │   ├── auth.py
│   │   ├── farms.py
│   │   ├── analysis.py
│   │   ├── results.py
│   │   ├── alerts.py
│   │   ├── reports.py
│   │   ├── prices.py
│   │   ├── catalog.py
│   │   ├── health.py
│   │   └── notifications.py
│   ├── models/             # SQLAlchemy ORM (User, Farm, Analysis, ...)
│   ├── schemas/            # Pydantic input/output
│   └── services/           # Lógica de negocio
│       ├── zonal_extraction.py
│       ├── report_service.py
│       └── notification_service.py
├── tests/                  # pytest
├── requirements.txt        # Dependencias pip
├── pyproject.toml          # Config moderna (ruff, pytest, setuptools)
└── .env.example
```

## Desarrollo

```bash
# 1. Setup
bash scripts/setup/setup-backend.sh    # crea venv + pip install

# 2. Iniciar
bash scripts/dev/start-backend.sh      # uvicorn --reload en :8000

# 3. Tests
bash scripts/test/test-backend.sh
```

## Entry point

```bash
cd apps/api
source venv/bin/activate
uvicorn sembraria.main:app --reload --host 0.0.0.0 --port 8000
```

## Configuración

Variables en `apps/api/.env.example`. Las críticas:

```env
DATABASE_URL=postgresql+psycopg2://sembriaia:sembriaia@localhost:5432/sembriaia
JWT_SECRET=<random-32-chars>
RASTER_INPUTS_DIR=../../data/inputs
RASTER_OUTPUTS_DIR=../../data/outputs
NOTIFICATIONS_MOCK=true
CORS_ORIGINS=http://localhost:5173
```

`BASE_DIR` en `sembraria/config.py` se calcula relativo al archivo:

```python
BASE_DIR = Path(__file__).resolve().parents[3]  # apps/api/sembraria/ -> 3 niveles
```

Así que `config/catalog/` y `data/` se resuelven relativos a la raíz del proyecto.
