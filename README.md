# SembrarIA

**Del pasto al plato.** Plataforma web que identifica la aptitud agrícola de fincas en Caquetá, Colombia, usando datos satelitales Copernicus y modelos de IA entrenados offline.

Hackathon CopernicusLAC 2026 · Universidad de la Amazonía

---

## ¿Qué es?

SembrarIA ayuda a productores, cooperativas y extensionistas de Caquetá a responder: **¿qué puedo sembrar en mi finca, y dónde exactamente?**

A partir de un polígono dibujado en el mapa, la plataforma:

1. Recorta rasters de aptitud pre-computados (cacao, plátano, yuca) al polígono de la finca.
2. Calcula hectáreas aptas vs. no aptas según criterios biofísicos.
3. Genera un mapa de oportunidad, una estimación económica y un PDF listo para crédito o trazabilidad EUDR.

---

## Estructura del monorepo

```
SembraIA/
├── apps/
│   ├── api/                         # Backend FastAPI
│   │   ├── sembraria/               # Paquete Python (uvicorn sembraria.main:app)
│   │   │   ├── main.py
│   │   │   ├── api/                 # 10 routers REST
│   │   │   ├── models/              # SQLAlchemy ORM
│   │   │   ├── schemas/             # Pydantic
│   │   │   └── services/            # zonal_extraction, report, notifications
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   ├── pyproject.toml
│   │   └── .env.example
│   │
│   └── web/                         # Frontend React
│       ├── public/                  # favicon, etc
│       ├── src/
│       │   ├── pages/               # 13 pantallas
│       │   ├── components/          # ui/, layout/, map/
│       │   ├── api/, store/, lib/, styles/
│       │   ├── App.jsx, main.jsx, config.js
│       ├── package.json, vite.config.js, tailwind.config.js
│       └── .env.example
│
├── config/                          # Fuente única de verdad
│   ├── catalog/                     # crops.yaml, geofence.yaml, raster.yaml
│   └── db/                          # 01_extensions.sql ... 06_seed_prices.sql
│
├── data/                            # Volumen volátil (gitignored)
│   ├── inputs/                      # 6 GeoTIFFs
│   └── outputs/                     # PNGs y PDFs generados
│
├── scripts/                         # Scripts cross-platform agrupados
│   ├── setup/                       # install-postgis, setup-{db,api,web}
│   ├── dev/                         # start-{api,web,all}, stop-all
│   ├── data/                        # generate-data, verify-inputs, _synthetic_rasters.py
│   └── test/                        # test-{api,web}, reset-db
│
├── docs/                            # Especificaciones
│   ├── architecture.md              # Decisiones de arquitectura
│   ├── mvp.md                       # Plan original 5 días
│   ├── design.md                    # 13 pantallas con prompts
│   └── data.md                      # Formato de los GeoTIFFs
│
├── .gitignore
├── LICENSE
└── README.md                        # Este archivo
```

**Por qué esta estructura:**
- `apps/` es el estándar moderno de monorepo (Turborepo, Nx, Google, Meta)
- El backend usa el layout canónico de FastAPI (`sembraria/` como paquete, `uvicorn sembraria.main:app`)
- Los scripts se agrupan por intención (setup/dev/data/test) — encuentras el script en <5 s
- Config, datos y código están separados claramente
- No hay carpetas vacías

---

## Requisitos

| Herramienta | Versión | Notas |
|-------------|---------|-------|
| Python | 3.11+ | Backend |
| Node.js | 20+ | Frontend |
| PostgreSQL | 16+ | Con extensión PostGIS |
| Git | cualquiera | Opcional |

> **No usa Docker, ni Redis, ni Celery.** El análisis es **sincrónico** (5-30 s) y la app corre 100% nativa.

---

## Instalación rápida (Windows)

```cmd
scripts\setup\install-postgis.bat
scripts\setup\setup-db.bat
scripts\setup\setup-backend.bat
scripts\setup\setup-frontend.bat
scripts\data\generate-data.bat
scripts\dev\start-all.bat
```

## Instalación rápida (Linux / macOS)

```bash
./scripts/setup/install-postgis.sh   # solo Linux
./scripts/setup/setup-db.sh
./scripts/setup/setup-backend.sh
./scripts/setup/setup-frontend.sh
./scripts/data/generate-data.sh
./scripts/dev/start-all.sh
```

Después:
- Frontend: <http://localhost:5173>
- API docs: <http://localhost:8000/docs>

---

## Variables de entorno

Cada app tiene su propio `.env.example`:

- `apps/api/.env.example` — backend (DATABASE_URL, JWT_SECRET, etc)
- `apps/web/.env.example` — frontend (VITE_API_URL, VITE_MAP_TILES_URL, etc)

Copia cada uno a `.env` en la misma ubicación y rellena los valores.

---

## Endpoints principales

| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/api/v1/health` | Liveness |
| GET | `/api/v1/catalog/crops` | Catálogo de cultivos |
| GET | `/api/v1/catalog/geofence` | Geofence de Caquetá |
| POST | `/api/v1/auth/register` | Registro |
| POST | `/api/v1/auth/login` | Login (devuelve JWT) |
| GET | `/api/v1/auth/me` | Usuario actual |
| GET/POST | `/api/v1/farms` | CRUD de fincas |
| POST | `/api/v1/analysis/farms/{id}/analyze` | **Análisis sincrónico** |
| GET | `/api/v1/results/{id}` | Resultado + criterios |
| GET | `/api/v1/reports/{id}/download` | PDF con ReportLab |
| GET | `/api/v1/alerts` | Alertas del usuario |
| GET | `/api/v1/prices/market-prices` | Precios actuales |

Documentación interactiva: <http://localhost:8000/docs>

---

## Rasters requeridos

`scripts/data/generate-data.bat` crea los 6 GeoTIFFs sintéticos en `data/inputs/`. Para producción, reemplázalos con la salida real del pipeline E3–E8:

```
data/inputs/
├── aptitud_CACAO.tif             # boolean 0/1 por píxel
├── aptitud_PLATANO.tif
├── aptitud_YUCA.tif
├── clasificacion_5clases.tif     # 0=pasto, 1=bosque, 2=cultivo, 3=agua, 4=urbano
├── sintesis_mejor_cultivo.tif    # ver leyenda en config/catalog/crops.yaml
└── stack_54features.tif          # stack multi-temporal (solo validación)
```

**Resolución del demo:** 500 m / píxel. **Producción:** 30 m / píxel (config en `config/catalog/raster.yaml`).

---

## Flujo de demo (3 minutos)

1. **Landing** → *Analizar mi finca gratis* → registro.
2. **Dashboard** → *Crear primera finca* o el icono de mapa.
3. **Analizar finca** → *Usar polígono demo (Florencia)* → completar nombre → *Analizar*.
4. **Resultado** (5-30 s) → ver mapa de oportunidad, criterios y potencial económico.
5. **Descargar PDF** → entregar a extensionista o banco.

---

## Decisiones de arquitectura

Ver [`docs/architecture.md`](./docs/INTEGRATION_GUIDE.md) para el detalle. Resumen:

- **Sin Celery/Redis**: análisis sincrónico en `POST /analysis/farms/{id}/analyze`. Timeout HTTP cliente 130 s.
- **El modelo se entrena offline** (E3–E8). El worker solo hace extracción zonal con `rasterio.mask`.
- **PostGIS valida geofence** vía la función `is_within_caqueta()`.
- **Notificaciones mock** por defecto. SMTP/Twilio activables con `NOTIFICATIONS_MOCK=false`.
- **Mobile-first**: breakpoints 393 / 768 / 1440. Sidebar colapsable en móvil.
- **Paquete Python `sembraria/`** con entry `uvicorn sembraria.main:app --app-dir apps/api`.

---

## Comandos útiles

```cmd
scripts\test\reset-db.bat           # DROP + recreate + reseed
scripts\test\test-backend.bat       # pytest
scripts\test\test-frontend.bat      # vitest
scripts\data\verify-inputs.bat      # Confirma 6 .tif en data/inputs/
scripts\dev\stop-all.bat            # Mata uvicorn y vite
```

```bash
# Acceso directo a la DB
psql -U sembriaia -d sembriaia -h localhost
```

---

## Licencia

MIT — Universidad de la Amazonía · CopernicusLAC Hackathon 2026

Datos Copernicus (Sentinel-1, Sentinel-2, ERA5) abiertos bajo la licencia oficial de la UE.
