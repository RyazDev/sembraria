# Guía de Integración — SembrarIA Frontend ↔ Backend

> **Para el compañero de frontend**: Este documento describe TODO lo que necesitas
> saber para conectar tu app web con el backend de SembrarIA. Léelo completo antes
> de empezar a integrar.
>
> **Versión del backend**: 1.0.0 · **Fecha**: 2026-06-03 · **Stack**: FastAPI 0.115 + PostgreSQL 18 + PostGIS 3.6 + React/Vite (frontend separado)

---

## Tabla de contenidos

1. [¿Qué es SembrarIA?](#1-qué-es-sembraría)
2. [Arquitectura general](#2-arquitectura-general)
3. [Prerrequisitos — qué instalar](#3-prerrequisitos--qué-instalar)
4. [Credenciales de la base de datos](#4-credenciales-de-la-base-de-datos)
5. [Levantar el backend desde cero](#5-levantar-el-backend-desde-cero)
6. [Levantar el frontend](#6-levantar-el-frontend)
7. [Modelo de datos (entidades y relaciones)](#7-modelo-de-datos-entidades-y-relaciones)
8. [Esquema de autenticación (JWT)](#8-esquema-de-autenticación-jwt)
9. [Referencia completa de endpoints](#9-referencia-completa-de-endpoints)
10. [Modelo de honestidad / provenancia de datos](#10-modelo-de-honestidad--provenancia-de-datos)
11. [Manejo de errores](#11-manejo-de-errores)
12. [Probar la integración end-to-end](#12-probar-la-integración-end-to-end)
13. [Problemas comunes (pitfalls)](#13-problemas-comunes-pitfalls)
14. [Resumen rápido (cheatsheet)](#14-resumen-rápido-cheatsheet)

---

## 1. ¿Qué es SembrarIA?

App del **Hackathon CopernicusLAC 2026** (Universidad de la Amazonía). Un productor
en Caquetá dibuja su finca en un mapa, y el sistema le dice qué porcentaje de su
tierra es apta para sembrar **cacao**, **plátano** o **yuca** — usando rasters
satelitales pre-calculados de las etapas E3-E8 (no es ML en tiempo real, es
**extracción zonal** de un raster binario de aptitud por cultivo).

**Datos del MVP**:
- 1 finca demo precargada: **Finca La Esperanza** (Florencia, 123.04 ha)
- 2 usuarios demo (ver §4)
- 3 alertas demo, 15 precios de mercado (todos marcados como `is_synthetic=true` —
  son **datos demo**, no scraping real)

---

## 2. Arquitectura general

```
┌──────────────────────────────────────────────────────────────────┐
│                       Frontend (Vite + React)                     │
│  - Login / Register                                                │
│  - Mapa interactivo (Leaflet o similar)                            │
│  - Dibuja polígono de la finca                                     │
│  - Tabla de alertas, gráficos de precios, descarga PDF            │
│                                                                       │
│  HTTP / JSON sobre http://localhost:5173                            │
└───────────────────────────┬──────────────────────────────────────────┘
                            │  fetch() con header
                            │  Authorization: Bearer <jwt>
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│              Backend FastAPI (puerto 8001 en este entorno)         │
│                                                                       │
│  Rutas (todas bajo /api/v1):                                        │
│    /auth/*        JWT, bcrypt 12 rounds                             │
│    /farms/*       CRUD de fincas (PostGIS POLYGON)                 │
│    /analysis/*    Análisis sincrónico de aptitud                    │
│    /results/*     PNG, criterios, resumen                           │
│    /reports/*     Generación/descarga de PDF                        │
│    /alerts/*      Alertas climáticas/deforestación/precio          │
│    /prices/*      Precios de mercado (con provenancia)             │
│    /notifications/*  Estado SMTP/SMS (mock por defecto)             │
│    /audit/*       Log de eventos (RBAC: extensionista+)             │
│    /catalog/*     Catálogos: crops, geofence, raster                 │
│    /health        Health check completo (DB, PostGIS, rasters)      │
│                                                                       │
│  Middlewares:                                                        │
│    - SecurityHeaders (X-Frame-Options, X-Content-Type-Options)     │
│    - RequestID (X-Request-Id para trazabilidad)                      │
│    - CORS (localhost:5173, localhost:3000, 127.0.0.1:5173)           │
│    - Rate limiting (slowapi) en /auth/login: 10 req/min por IP       │
└───────────────────────────┬──────────────────────────────────────────┘
                            │  SQLAlchemy 2.0 + GeoAlchemy2
                            │  psycopg2 driver
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│           PostgreSQL 18 + PostGIS 3.6 (puerto 5432)                │
│  DB: sembraria        User: postgres        Password: 1234          │
│                                                                       │
│  Esquema: 10 tablas en `public` + 2 en `topology` (PostGIS)        │
│  Fuente de verdad: config/db/01..09_*.sql (idempotentes)            │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Almacenamiento de archivos (sistema de archivos local)             │
│  /data/inputs/    → GeoTIFFs de aptitud pre-calculados              │
│  /data/outputs/   → PNG/PDF generados por análisis                  │
│  Servidos en HTTP bajo /static/                                    │
└──────────────────────────────────────────────────────────────────┘
```

**Punto clave**: el backend NO re-entrena modelos. El "análisis" es solo un
recorte del raster pre-calculado de aptitud (ya en disco) con la geometría
de la finca, en **~0.5-5 segundos**.

---

## 3. Prerrequisitos — qué instalar

Para correr el backend **necesitas** instalado en tu máquina:

| Componente        | Versión mínima | ¿Por qué?                                    | Cómo verificar                   |
|-------------------|----------------|----------------------------------------------|----------------------------------|
| **PostgreSQL**    | 13+ (probado con 18) | Motor de base de datos                       | `psql --version`                |
| **PostGIS**       | 3.x            | Geometría POLYGON, función `is_within_caqueta` | `psql -c "SELECT PostGIS_Version();"` |
| **Python**        | 3.12+          | Runtime del backend                          | `python --version`               |
| **Node.js**       | 20+ (solo frontend) | Runtime del frontend                       | `node --version`                 |
| **pip**           | 23+            | Instalador de paquetes Python                | `pip --version`                  |
| **Git**           | cualquiera      | Clonar el repo                               | `git --version`                  |

### 3.1 Instalar PostgreSQL + PostGIS en Windows

1. Descarga el instalador: <https://www.enterprisedb.com/downloads/postgres-postgresql-downloads>
2. Durante la instalación:
   - **Anota la contraseña del usuario `postgres`** (la necesitarás en §4)
   - En la pantalla de "Select Components" **marca PostGIS** (es una opción separada)
   - Puerto: deja **5432** (default)
3. Al terminar, abre **SQL Shell (psql)** o **pgAdmin** y verifica:
   ```sql
   SELECT version();
   SELECT PostGIS_Version();
   ```
   Deben devolver un string de versión cada uno.

### 3.2 Instalar PostgreSQL + PostGIS en Linux/WSL/Mac

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y postgresql postgresql-contrib postgis

# Mac (con Homebrew)
brew install postgresql postgis
```

---

## 4. Credenciales de la base de datos

> **Estas son las credenciales que usa el backend en este entorno. Si tu compañero
> las cambió en su `.env`, respétalas. Las de abajo son los defaults del proyecto.**

```
Host:     localhost
Puerto:   5432
Usuario:  postgres
Password: 1234
Database: sembraria
```

**Connection string completo** (lo que va en `DATABASE_URL`):
```
postgresql+psycopg2://postgres:1234@localhost:5432/sembraria
```

### Usuarios de la app (login web)

| Email                              | Password         | Rol            | Notas                              |
|------------------------------------|------------------|----------------|------------------------------------|
| `productor@sembraria.demo`         | `sembraria2026`  | `productor`    | Productor con 1 finca demo         |
| `cooperativa@sembraria.demo`       | `sembraria2026`  | `cooperativa`  | Cooperativa Multiactiva El Doncello |

> Los passwords están hasheados con **bcrypt 12 rounds** en la base de datos.
> El hash es: `$2b$12$HNZsb40WZodQ2Cmv98RDbu3BshGOacPX7pHJ9gS31Jl3Z3iDmaaA2`

### Finca demo precargada

| ID                                     | Nombre             | Municipio  | Área (ha) | Geometría         |
|----------------------------------------|--------------------|------------|-----------|--------------------|
| `aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa` | Finca La Esperanza | Florencia  | 123.04    | POLYGON 4326      |

Las coordenadas aproximadas del polígono: lon `[-75.62, -75.61]`, lat `[1.61, 1.62]`.

---

## 5. Levantar el backend desde cero

### Opción A — Script automatizado (recomendado para tu compañero)

Hay un script que hace todo: instala PostGIS, crea la DB, corre las migraciones:

```bash
# Windows (CMD o PowerShell)
scripts\setup\setup-db.bat

# Linux / Mac / WSL
bash scripts/setup/setup-db.sh
```

El script:
1. Verifica que `psql` esté en el PATH
2. Verifica que PostGIS esté disponible
3. Pide credenciales de postgres (puede que ya estén en `.env`)
4. **DROP DATABASE** `sembraria` (reset, si existe)
5. **CREATE DATABASE** `sembraria`
6. Ejecuta los 9 scripts SQL en orden

### Opción B — Manual paso a paso

Si el script falla o quieres entender qué hace:

```bash
# 1. Abrir psql como postgres
psql -U postgres -h localhost
# Te pide la contraseña (1234 en este entorno)

# 2. (Opcional) Borrar la DB si existe
DROP DATABASE IF EXISTS sembraria;

# 3. Crear la DB
CREATE DATABASE sembraria;

# 4. Conectarse a la DB nueva
\c sembraria

# 5. Ejecutar los 9 scripts en orden
\i 'C:\Users\NITRO\Desktop\Proyecto\SembraIA\config\db\01_extensions.sql'
\i 'C:\Users\NITRO\Desktop\Proyecto\SembraIA\config\db\02_schema.sql'
\i 'C:\Users\NITRO\Desktop\Proyecto\SembraIA\config\db\03_indexes.sql'
\i 'C:\Users\NITRO\Desktop\Proyecto\SembraIA\config\db\04_caqueta_boundary.sql'
\i 'C:\Users\NITRO\Desktop\Proyecto\SembraIA\config\db\05_seed_users.sql'
\i 'C:\Users\NITRO\Desktop\Proyecto\SembraIA\config\db\06_seed_prices.sql'
\i 'C:\Users\NITRO\Desktop\Proyecto\SembraIA\config\db\07_audit_log.sql'
\i 'C:\Users\NITRO\Desktop\Proyecto\SembraIA\config\db\08_data_provenance.sql'
\i 'C:\Users\NITRO\Desktop\Proyecto\SembraIA\config\db\09_model_versioning.sql'

# 6. Verificar
\dt
-- Debe mostrar 10 tablas en public: users, farms, analyses, results,
-- alerts, market_prices, audit_log, caqueta_boundary, revoked_tokens, _db_migrations

SELECT count(*) FROM users;        -- debe ser 2
SELECT count(*) FROM farms;        -- debe ser 1
SELECT count(*) FROM alerts;       -- debe ser 3
SELECT count(*) FROM market_prices; -- debe ser 15
```

> **Los 9 scripts son idempotentes** (usan `CREATE TABLE IF NOT EXISTS`,
> `DO $$ ... EXCEPTION WHEN duplicate_object`, `ON CONFLICT DO NOTHING`).
> Puedes re-ejecutarlos sin miedo.

### 5.3 Instalar dependencias Python y arrancar el backend

```bash
# 1. Crear virtualenv (si no existe)
cd apps\api
python -m venv .venv

# 2. Activar (Windows)
.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Verificar que arranca
python -m sembraria.main
# Debe loguear: "Inicializando base de datos SembrarIA..." y luego "Base de datos lista."
# Servidor en http://127.0.0.1:8001

# 5. Probar
curl http://127.0.0.1:8001/api/v1/health
# Debe devolver JSON con status=ok
```

**Nota sobre el puerto**: en este entorno el backend corre en **8001** porque
el 8000 estaba ocupado. El frontend ya apunta a `VITE_API_URL=http://localhost:8001/api/v1`.
Si tu compañero quiere usar otro puerto, edita `API_PORT` en `.env` Y
`VITE_API_URL` en `apps/web/.env` con el mismo número.

### 5.4 Si todo va bien, debes ver

```json
{
  "status": "ok",
  "app": { "name": "SembrarIA", "version": "1.0.0", "env": "development" },
  "database": { "status": "ok", "version": "PostgreSQL 18.3 ...", "postgis_version": "3.6 ...", "migrations_applied": 9 },
  "rasters": { "aptitud_CACAO.tif": { "status": "ok", ... }, ... },
  "disk": { "status": "ok", "free_gb": 50.2, ... }
}
```

`status: "ok"` = todo en orden.
`status: "degraded"` = probablemente faltan rasters en `data/inputs/`.
`status: "error"` = la DB no responde.

---

## 6. Levantar el frontend

```bash
# 1. Instalar dependencias
cd apps\web
npm install

# 2. Verificar .env
cat .env
# Debe contener:
#   VITE_API_URL=http://localhost:8001/api/v1
#   VITE_MAP_DEFAULT_CENTER_LON=-75.62
#   VITE_MAP_DEFAULT_CENTER_LAT=1.615

# 3. Arrancar dev server
npm run dev
# Disponible en http://localhost:5173
```

Si todo va bien, la app carga en `http://localhost:5173` y te muestra el
formulario de login. Loguéate con `productor@sembraria.demo` / `sembraria2026`.

---

## 7. Modelo de datos (entidades y relaciones)

### Diagrama de entidades

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  users   │ 1───∞  │  farms   │ 1───∞  │analyses  │
│          │         │          │         │          │
│  id      │         │  id      │         │  id      │
│  email   │         │  user_id │         │  farm_id │
│  role    │         │  geom    │         │  user_id │
│  pass    │         │  area_ha │         │  cultivo │
└────┬─────┘         └────┬─────┘         │  status  │
     │                   │                 └────┬─────┘
     │ 1                  │ 0..1                │ 1
     │                    │                     │
     │ ∞                  │ ∞                   │ 1
     │                    │                     │
┌────▼─────┐         ┌────▼─────┐         ┌────▼─────┐
│  alerts  │ ∞───1   │  farms   │         │ results  │
│          │         │          │         │          │
│  id      │         │          │         │analysis_id│
│  user_id │         │          │         │png_path  │
│  farm_id │         │          │         │model_ver │
│  type    │         │          │         │criteria  │
│  is_synth│         │          │         │          │
└──────────┘         └──────────┘         └──────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│market_prices │    │  audit_log   │    │   farms      │
│              │    │              │    │  (geometría) │
│  id (uuid)   │    │  id          │    │  geom:       │
│  producto    │    │  user_id     │    │  GEOMETRY    │
│  precio_cop  │    │  action      │    │  (POLYGON,   │
│  is_synthetic│    │  resource    │    │   4326)      │
│  source_url  │    │  request_id  │    └──────────────┘
│              │    │  details     │
│ (sin FK a    │    │  (jsonb)     │    ┌──────────────┐
│  otras       │    │              │    │caqueta_      │
│  tablas)     │    │              │    │  boundary    │
└──────────────┘    └──────────────┘    │  (geofence)  │
                                        └──────────────┘
```

### Tabla `users`
| Columna               | Tipo                       | Notas                                    |
|-----------------------|----------------------------|------------------------------------------|
| `id`                  | UUID PK                    | `gen_random_uuid()` default              |
| `email`               | VARCHAR(255) UNIQUE NOT NULL|                                         |
| `phone`               | VARCHAR(20)                |                                          |
| `full_name`           | VARCHAR(255) NOT NULL      |                                          |
| `hashed_password`     | VARCHAR(255) NOT NULL      | bcrypt 12 rounds                         |
| `role`                | `user_role` ENUM           | `productor\|cooperativa\|extensionista\|gobierno` |
| `organization`        | VARCHAR(255)               |                                          |
| `is_active`           | BOOLEAN                    | default `true`                           |
| `sms_notifications`   | BOOLEAN                    | default `false`                          |
| `email_notifications` | BOOLEAN                    | default `true`                           |
| `whatsapp_notifications`| BOOLEAN                   | default `false`                          |
| `created_at`          | TIMESTAMPTZ                | default `now()`                          |
| `updated_at`          | TIMESTAMPTZ                | auto-actualizado por trigger              |

### Tabla `farms`
| Columna     | Tipo                          | Notas                                    |
|-------------|-------------------------------|------------------------------------------|
| `id`        | UUID PK                       |                                          |
| `user_id`   | UUID FK→users.id ON DELETE CASCADE |                                  |
| `name`      | VARCHAR(255) NOT NULL         |                                          |
| `municipio` | VARCHAR(100) NOT NULL         |                                          |
| `geom`      | GEOMETRY(POLYGON, 4326) NOT NULL| SRID 4326 = WGS84 (lon/lat)            |
| `area_ha`   | NUMERIC(10,2) NOT NULL        | CHECK > 0, calculado server-side en `ST_Area` (EPSG:3116) |
| `status`    | `farm_status` ENUM            | `activa\|en_analisis\|inactiva`          |
| `notes`     | TEXT                          |                                          |
| `created_at`| TIMESTAMPTZ                   |                                          |
| `updated_at`| TIMESTAMPTZ                   |                                          |

### Tabla `analyses`
| Columna            | Tipo                          | Notas                              |
|--------------------|-------------------------------|------------------------------------|
| `id`               | UUID PK                       |                                    |
| `farm_id`          | UUID FK→farms.id              |                                    |
| `user_id`          | UUID FK→users.id              |                                    |
| `cultivo`          | VARCHAR(50) NOT NULL          | `cacao\|platano\|yuca`             |
| `status`           | `analysis_status` ENUM        | `pending\|processing\|completed\|failed` |
| `hectares_aptas`   | NUMERIC(10,2)                 |                                    |
| `hectares_totales` | NUMERIC(10,2)                 |                                    |
| `porcentaje_apto`  | NUMERIC(5,2)                  |                                    |
| `criterios`        | JSONB                         | detalles de la extracción zonal    |
| `execution_time_ms`| INTEGER                       |                                    |
| `error_message`    | TEXT                          | solo si `status=failed`            |
| `created_at`       | TIMESTAMPTZ                   |                                    |
| `completed_at`     | TIMESTAMPTZ                   |                                    |

### Tabla `results`
| Columna           | Tipo                       | Notas                                  |
|-------------------|----------------------------|----------------------------------------|
| `id`              | UUID PK                    |                                        |
| `analysis_id`     | UUID UNIQUE FK→analyses.id | relación 1-a-1 con analysis            |
| `png_path`        | VARCHAR(500)               | ruta absoluta al PNG generado          |
| `pdf_path`        | VARCHAR(500)               | ruta absoluta al PDF                   |
| `geojson_path`    | VARCHAR(500)               | ruta absoluta al GeoJSON               |
| `png_url`         | VARCHAR(500)               | URL relativa servida por el backend    |
| `summary`         | JSONB                      | resumen legible para UI                |
| `criteria`        | JSONB                      | criterios detallados                   |
| `slope_breakdown` | JSONB                      | desglose por pendiente                 |
| `model_version`   | VARCHAR(32)                | `v1.1.0` (semver)                      |
| `model_algorithm` | VARCHAR(64)                | `zonal_majority_v1`                    |
| `raster_inputs`   | JSONB                      | snapshot de los rasters usados         |
| `config_snapshot` | JSONB                      | snapshot de la config al correr        |
| `created_at`      | TIMESTAMPTZ                |                                        |

### Tabla `alerts`
| Columna             | Tipo                            | Notas                          |
|---------------------|---------------------------------|--------------------------------|
| `id`                | UUID PK                         |                                |
| `user_id`           | UUID FK→users.id                |                                |
| `farm_id`           | UUID FK→farms.id NULL           | puede ser global (no atada a finca) |
| `type`              | `alert_type` ENUM               | `estres_hidrico\|deforestacion\|precio\|clima\|normal` |
| `severity`          | `alert_severity` ENUM           | `critica\|alta\|media\|baja`    |
| `title`             | VARCHAR(255) NOT NULL           |                                |
| `message`           | TEXT NOT NULL                   |                                |
| `affected_hectares` | NUMERIC(10,2) NULL              |                                |
| `is_read`           | BOOLEAN                         | default `false`                |
| `is_synthetic`      | BOOLEAN                         | default `true` (datos demo)    |
| `metadata`          | JSONB                           |                                |
| `created_at`        | TIMESTAMPTZ                     |                                |
| `read_at`           | TIMESTAMPTZ NULL                |                                |

### Tabla `market_prices`
| Columna             | Tipo                | Notas                                |
|---------------------|---------------------|--------------------------------------|
| `id`                | UUID PK             |                                      |
| `producto`          | VARCHAR(50) NOT NULL| `cacao\|platano\|yuca\|panela\|...`  |
| `precio_cop_kg`     | NUMERIC(12,2) NOT NULL|                                    |
| `unidad`            | VARCHAR(20)         | default `COP/kg`                     |
| `fuente`            | VARCHAR(100)        | `FEDECACAO`, `MinAgricultura`, etc.  |
| `cambio_porcentual` | NUMERIC(5,2) NULL   |                                      |
| `municipio`         | VARCHAR(100) NULL   |                                      |
| `recorded_at`       | TIMESTAMPTZ         |                                      |
| `is_synthetic`      | BOOLEAN             | default `true` (datos demo)          |
| `source_url`        | TEXT NULL           | URL real si `is_synthetic=false`     |
| `fetched_at`        | TIMESTAMPTZ NULL    |                                      |

### Tabla `audit_log`
| Columna        | Tipo                          | Notas                              |
|----------------|-------------------------------|------------------------------------|
| `id`           | UUID PK                       |                                    |
| `user_id`      | UUID FK→users.id NULL         | puede ser NULL (login fallido)     |
| `action`       | VARCHAR(64) NOT NULL          | verbo en pasado: `login`, `create_farm`, etc. |
| `resource`     | VARCHAR(64) NOT NULL          | tipo: `user`, `farm`, `analysis`   |
| `resource_id`  | VARCHAR(64) NULL              |                                    |
| `ip_address`   | INET NULL                     |                                    |
| `user_agent`   | VARCHAR(500) NULL             |                                    |
| `request_id`   | VARCHAR(64) NULL              | correlacionado con `X-Request-Id`  |
| `details`      | JSONB NULL                    | metadata extra                     |
| `created_at`   | TIMESTAMPTZ                   |                                    |

### ENUMs

| Enum              | Valores                                                                |
|-------------------|------------------------------------------------------------------------|
| `user_role`       | `productor`, `cooperativa`, `extensionista`, `gobierno`                |
| `farm_status`     | `activa`, `en_analisis`, `inactiva`                                    |
| `analysis_status` | `pending`, `processing`, `completed`, `failed`                         |
| `alert_type`      | `estres_hidrico`, `deforestacion`, `precio`, `clima`, `normal`         |
| `alert_severity`  | `critica`, `alta`, `media`, `baja`                                     |

### Tablas auxiliares (no expuestas vía API)

- **`caqueta_boundary`** — multipolígono del departamento (bbox aproximado).
  Usado por la función `is_within_caqueta(geom)` que valida al crear fincas.
- **`revoked_tokens`** — tokens JWT invalidados (para logout). No implementado
  en el MVP actual pero la tabla existe.
- **`_db_migrations`** — registro de qué scripts SQL ya se aplicaron (usado por
  el `init_db.py` al boot del backend para idempotencia).

---

## 8. Esquema de autenticación (JWT)

### Flujo de login

```
[Frontend]                          [Backend]
    │                                    │
    │  POST /api/v1/auth/login           │
    │  { email, password }               │
    │ ─────────────────────────────────► │
    │                                    │  1. Busca usuario por email
    │                                    │  2. Verifica password con bcrypt
    │                                    │  3. Genera JWT firmado (HS256)
    │                                    │  4. Loguea evento "login" en audit_log
    │                                    │
    │  200 OK                            │
    │  { access_token, user }            │
    │ ◄───────────────────────────────── │
    │                                    │
    │  Guarda access_token en memoria    │
    │  o sessionStorage                  │
```

### Estructura del JWT

Header:
```json
{ "alg": "HS256", "typ": "JWT" }
```

Payload:
```json
{
  "sub": "11111111-1111-1111-1111-111111111111",  // user.id (UUID)
  "exp": 1717410000,                              // expira en 24h
  "iat": 1717323600,                              // emitido en
  "nbf": 1717323600,                              // válido desde
  "kid": "v2",                                    // key id (rotación)
  "role": "productor"                             // extra claim
}
```

### Cómo enviar el token

Todas las requests autenticadas requieren el header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Refresh / expiración

- **El token expira en 24h** (configurable en `.env` con `JWT_EXPIRE_HOURS`).
- **No hay endpoint de refresh**: el frontend debe re-loguear al expirar.
- Cuando llega un 401, el frontend debe limpiar el token y redirigir a login.

### Logout

- **No hay endpoint de logout** en el MVP.
- El frontend simplemente borra el token del storage. El token seguirá siendo
  válido técnicamente hasta su `exp`, pero el backend no lo re-vocará (la tabla
  `revoked_tokens` existe para futuro).

### Rate limiting

- `POST /api/v1/auth/login` está limitado a **10 requests por minuto por IP**.
- Si excedes, recibes `429 Too Many Requests` con un `Retry-After` header.
- En login normal no deberías dispararlo (máx 1-2 por minuto).

---

## 9. Referencia completa de endpoints

**Base URL**: `http://localhost:8001/api/v1`

Todos los endpoints marcados con 🔒 requieren header `Authorization: Bearer <jwt>`.

### 9.1 Health

#### `GET /health` (público)
Health check completo: app + DB + PostGIS + rasters + disco.

**Response 200**:
```json
{
  "status": "ok",
  "app": { "name": "SembrarIA", "version": "1.0.0", "env": "development" },
  "database": {
    "status": "ok",
    "version": "PostgreSQL 18.3 ...",
    "postgis_version": "3.6 USE_GEOS=1 ...",
    "migrations_applied": 9
  },
  "rasters": {
    "aptitud_CACAO.tif": { "status": "ok", "size_mb": 1.2, "bands": 1, "width": 100, "height": 100, "crs": "EPSG:4326" },
    "aptitud_PLATANO.tif": { "status": "ok", ... },
    "aptitud_YUCA.tif": { "status": "ok", ... },
    "clasificacion_5clases.tif": { "status": "ok", ... },
    "sintesis_mejor_cultivo.tif": { "status": "ok", ... },
    "stack_54features.tif": { "status": "ok", ... }
  },
  "disk": { "status": "ok", "free_gb": 50.2, "percent_used": 45.0 },
  "timestamp": "2026-06-03T12:34:56.789+00:00"
}
```

#### `GET /health/ready` (público)
Readiness probe (solo DB).
```json
{ "ready": true, "database": "ok" }
```

#### `GET /health/live` (público)
Liveness probe (solo proceso vivo).
```json
{ "alive": true }
```

### 9.2 Auth

#### `POST /auth/register` (público)
Registra un nuevo usuario y devuelve JWT (auto-login).

**Request**:
```json
{
  "email": "usuario@example.com",
  "password": "mipassword",
  "full_name": "Nombre Completo",
  "phone": "+573001234567",         // opcional
  "role": "productor",              // productor | cooperativa | extensionista | gobierno
  "organization": "Mi org"          // opcional
}
```

**Response 201**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "usuario@example.com",
    "full_name": "Nombre Completo",
    "role": "productor",
    "is_active": true,
    ...
  }
}
```

**Errores**:
- `400`: email ya registrado

#### `POST /auth/login` (público, rate-limited 10/min)
Inicia sesión.

**Request**:
```json
{ "email": "productor@sembraria.demo", "password": "sembraria2026" }
```

**Response 200**:
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": { "id": "...", "email": "...", "role": "productor", ... }
}
```

**Errores**:
- `401`: email o password incorrectos
- `403`: usuario inactivo (`is_active=false`)
- `429`: demasiados intentos (espera 60s)

#### `GET /auth/me` 🔒
Devuelve el usuario actual.

**Response 200**:
```json
{
  "id": "11111111-1111-1111-1111-111111111111",
  "email": "productor@sembraria.demo",
  "full_name": "Brayan Cuellar",
  "role": "productor",
  "organization": "UDLA Raices",
  "is_active": true,
  "phone": "+573001234567",
  "email_notifications": true,
  ...
}
```

### 9.3 Farms

#### `GET /farms` 🔒
Lista las fincas del usuario actual.

**Response 200**: array de `FarmOut`:
```json
[
  {
    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "user_id": "11111111-1111-1111-1111-111111111111",
    "name": "Finca La Esperanza",
    "municipio": "Florencia",
    "geom": { "type": "Polygon", "coordinates": [[[-75.62, 1.61], ...]] },
    "area_ha": 123.04,
    "status": "activa",
    "notes": "Finca demo de cacao",
    "created_at": "2026-06-01T...",
    "updated_at": "2026-06-01T..."
  }
]
```

#### `POST /farms` 🔒
Crea una nueva finca.

**Request**:
```json
{
  "name": "Mi nueva finca",
  "municipio": "Florencia",
  "geom": {
    "type": "Polygon",
    "coordinates": [[[-75.62, 1.61], [-75.61, 1.61], [-75.61, 1.62], [-75.62, 1.62], [-75.62, 1.61]]]
  },
  "notes": "Para cacao"
}
```

> **Importante**: el `area_ha` lo calcula el backend automáticamente desde
> la geometría usando PostGIS (`ST_Area` en EPSG:3116). No lo envíes en el
> body — se ignora o se sobreescribe.

**Response 201**: `FarmOut` con `area_ha` calculado.

**Errores**:
- `400`: el polígono está fuera de Caquetá (valida con `is_within_caqueta`)
- `400`: el área es < 0.1 ha o > 1000 ha
- `422`: la geometría no es un POLYGON válido

#### `GET /farms/{farm_id}` 🔒
Devuelve una finca por ID.

#### `PUT /farms/{farm_id}` 🔒
Actualiza una finca (campos parciales OK).

**Request** (todos los campos son opcionales):
```json
{
  "name": "...",
  "municipio": "...",
  "notes": "...",
  "geom": { ... }  // si se cambia, area_ha se recalcula
}
```

#### `DELETE /farms/{farm_id}` 🔒
Borra la finca (cascadea a analyses, results, alerts asociadas).

**Response 204**: no content.

### 9.4 Analysis

#### `GET /analysis?farm_id={uuid}` 🔒
Lista análisis del usuario (opcionalmente filtrados por `farm_id`).

#### `GET /analysis/{analysis_id}` 🔒
Devuelve un análisis.

**Response 200**:
```json
{
  "id": "...",
  "farm_id": "...",
  "user_id": "...",
  "cultivo": "cacao",
  "status": "completed",
  "hectares_aptas": 98.4,
  "hectares_totales": 123.04,
  "porcentaje_apto": 80.0,
  "criterios": {
    "raster": "aptitud_CACAO.tif",
    "pixels_aptos": 3936,
    "pixels_totales": 4921,
    "pixel_size_m": 25.0,
    "model_version": "v1.1.0",
    "model_algorithm": "zonal_majority_v1"
  },
  "execution_time_ms": 1234,
  "error_message": null,
  "created_at": "...",
  "completed_at": "..."
}
```

#### `POST /analysis/farms/{farm_id}/analyze` 🔒
Ejecuta un análisis **sincrónico** (~0.5-5 segundos).

**Request**:
```json
{ "cultivo": "cacao" }  // "cacao" | "platano" | "yuca"
```

**Response 200**: `AnalysisOut` (igual estructura que GET /analysis/{id}).

**Errores**:
- `400`: cultivo no soportado
- `404`: finca no encontrada
- `403`: la finca no es tuya
- `500`: error en el procesamiento (ej: raster no disponible)

> El endpoint es **sincrónico** en este MVP: esperas la respuesta y ya
> tienes los resultados. No hay webhooks ni polling.

### 9.5 Results

#### `GET /results/{analysis_id}` 🔒
Devuelve el resultado detallado de un análisis.

**Response 200**:
```json
{
  "id": "...",
  "analysis_id": "...",
  "png_path": "C:\\...\\outputs\\cacao\\uuid.png",
  "png_url": "/static/cacao/uuid.png",
  "summary": {
    "hectares_aptas": 98.4,
    "hectares_totales": 123.04,
    "porcentaje_apto": 80.0,
    "cultivo": "cacao",
    "model_version": "v1.1.0"
  },
  "criteria": { ... },
  "slope_breakdown": { ... },
  "model_version": "v1.1.0",
  "model_algorithm": "zonal_majority_v1",
  "raster_inputs": [{ "name": "aptitud_CACAO.tif", "purpose": "suitability_mask", "synthetic": true }],
  "config_snapshot": { ... },
  "created_at": "..."
}
```

#### `GET /results/{analysis_id}/png` 🔒
Devuelve el PNG generado (Content-Type: `image/png`).

El frontend puede usar la URL directamente:
```html
<img src="http://localhost:8001/api/v1/results/{analysis_id}/png" />
```
(También necesita el header Authorization — usar fetch+blob o service worker)

> Truco: para mostrar en `<img>` sin header, primero hace fetch con auth,
> conviertes a blob URL, y asignas a `img.src`.

### 9.6 Reports

#### `GET /reports/{analysis_id}/download` 🔒
Genera y descarga el PDF del análisis.

**Response 200**: `application/pdf` (streaming).

> La primera vez puede tardar 1-2 segundos en generar el PDF. Después queda
> cacheado en disco.

### 9.7 Alerts

#### `GET /alerts?type=...&is_read=...` 🔒
Lista alertas del usuario actual.

**Query params** (todos opcionales):
- `type`: `estres_hidrico` | `deforestacion` | `precio` | `clima` | `normal`
- `is_read`: `true` | `false`

**Response 200**: array de `AlertOut`:
```json
[
  {
    "id": "...",
    "user_id": "...",
    "farm_id": "...",
    "type": "estres_hidrico",
    "severity": "critica",
    "title": "Estres hidrico detectado",
    "message": "Riegue en las proximas 48 horas. ...",
    "affected_hectares": 3.2,
    "is_read": false,
    "is_synthetic": true,
    "metadata": null,
    "created_at": "...",
    "read_at": null
  }
]
```

#### `GET /alerts/unread-count` 🔒
```json
{ "unread": 2 }
```

#### `PUT /alerts/{alert_id}/read` 🔒
Marca como leída/no leída.

**Request**:
```json
{ "is_read": true }
```

**Response 200**: `AlertOut` actualizado (con `read_at` poblado si `is_read=true`).

### 9.8 Prices

#### `GET /prices/market-prices` 🔒
Devuelve el último precio registrado por cada producto.

**Response 200**:
```json
[
  {
    "producto": "cacao",
    "precio_cop_kg": 12500.0,
    "unidad": "COP/kg",
    "fuente": "FEDECACAO",
    "cambio_porcentual": 8.2,
    "municipio": "Nacional",
    "recorded_at": "2026-06-03T...",
    "is_synthetic": true,
    "source_url": null,
    "fetched_at": null
  },
  ...
]
```

> Todos los precios actuales en el seed son `is_synthetic=true`. La UI debe
> mostrar un banner honesto indicando que los precios son demo.

#### `GET /prices/market-prices/provenance` 🔒
Resumen de la procedencia de los datos.

**Response 200**:
```json
{
  "data_provenance": "synthetic",  // "synthetic" | "real" | "mixed" | "empty"
  "total": 15,
  "synthetic": 15,
  "real": 0,
  "message": "Los precios mostrados son DEMO (generados internamente). No usar para decisiones reales hasta conectar fuentes oficiales."
}
```

#### `GET /prices/market-prices/history/{producto}?days=30` 🔒
Histórico de precios de un producto.

**Response 200**:
```json
[
  { "precio_cop_kg": 11800.0, "recorded_at": "2026-05-31T...", "is_synthetic": true },
  { "precio_cop_kg": 12100.0, "recorded_at": "2026-06-01T...", "is_synthetic": true },
  { "precio_cop_kg": 12300.0, "recorded_at": "2026-06-02T...", "is_synthetic": true },
  { "precio_cop_kg": 12500.0, "recorded_at": "2026-06-03T...", "is_synthetic": true }
]
```

### 9.9 Notifications

#### `GET /notifications/status` (público)
Estado del subsistema SMTP/Twilio.

**Response 200**:
```json
{
  "smtp_configured": false,
  "smtp_host": "",
  "smtp_mock": true,
  "twilio_configured": false,
  "twilio_phone": "",
  "twilio_mock": true,
  "mode": "mock"  // "mock" | "live" | "mixed"
}
```

> `mode=mock` significa que los emails/SMS solo se imprimen en consola, no
> se envían. La UI debe mostrar un banner indicando esto.

#### `POST /notifications/notify-test` 🔒
Envía una notificación de prueba.

**Request**:
```json
{
  "to": "test@example.com",
  "subject": "Test",
  "message": "Hola desde SembrarIA",
  "channel": "email"  // "email" | "sms"
}
```

**Response 200**:
```json
{ "ok": true, "mock": true, "mode": "mock", "message": "Email logged (mock mode)" }
```

### 9.10 Audit (extensionistas+)

#### `GET /audit?user_id=...&action=...&resource=...&limit=100&offset=0` 🔒 🔐
Lista eventos del audit log.

**🔐 Requiere rol**: `extensionista`, `cooperativa` o `gobierno`. Un productor
recibe `403`.

**Response 200**: array de `AuditLogOut`:
```json
[
  {
    "id": "...",
    "user_id": "11111111-...",
    "action": "analyze_completed",
    "resource": "analysis",
    "resource_id": "...",
    "ip_address": "127.0.0.1",
    "user_agent": "Mozilla/5.0 ...",
    "request_id": "uuid-v4",
    "details": { "farm_id": "...", "cultivo": "cacao", "hectares_aptas": 98.4, "porcentaje_apto": 80.0 },
    "created_at": "..."
  }
]
```

#### `GET /audit/actions` 🔒 🔐
Lista las acciones únicas registradas (para construir filtros UI).

**Response 200**: `{ "actions": ["analyze_completed", "analyze_started", "login", "login_failed", "create_farm", "delete_farm", "update_farm"] }`

### 9.11 Catalog

#### `GET /catalog/crops` (público)
Catálogo de cultivos disponibles.

**Response 200**:
```json
{
  "crops": [
    {
      "id": "cacao",
      "name": "Cacao",
      "scientific_name": "Theobroma cacao",
      "description": "Cultivo perenne de alto valor...",
      "optimal_altitude_m": [200, 1200],
      "optimal_slope_pct": [0, 30],
      "rainfall_mm_year": [1500, 2500]
    },
    { "id": "platano", ... },
    { "id": "yuca", ... }
  ]
}
```

#### `GET /catalog/geofence` (público)
Geofence de Caquetá (polígono del departamento).

#### `GET /catalog/raster` (público)
Configuración de rasters (tamaños, paths, etc.).

#### `GET /catalog/all` (público)
Devuelve los tres catálogos juntos en una sola request.

### 9.12 Resumen tabular de endpoints

| Método | Ruta                              | Auth   | Rol requerido     | Descripción                          |
|--------|-----------------------------------|--------|-------------------|--------------------------------------|
| GET    | `/health`                         | público| -                 | Health completo                      |
| GET    | `/health/ready`                   | público| -                 | Solo DB                              |
| GET    | `/health/live`                    | público| -                 | Liveness                             |
| POST   | `/auth/register`                  | público| -                 | Registrar usuario                    |
| POST   | `/auth/login`                     | público| -                 | Login (rate-limited)                 |
| GET    | `/auth/me`                        | 🔒     | cualquiera        | Usuario actual                       |
| GET    | `/farms`                          | 🔒     | cualquiera        | Listar mis fincas                    |
| POST   | `/farms`                          | 🔒     | cualquiera        | Crear finca                          |
| GET    | `/farms/{id}`                     | 🔒     | dueño             | Ver finca                            |
| PUT    | `/farms/{id}`                     | 🔒     | dueño             | Actualizar finca                     |
| DELETE | `/farms/{id}`                     | 🔒     | dueño             | Borrar finca                         |
| GET    | `/analysis`                       | 🔒     | cualquiera        | Listar mis análisis                  |
| GET    | `/analysis/{id}`                  | 🔒     | dueño             | Ver análisis                         |
| POST   | `/analysis/farms/{farm_id}/analyze`| 🔒    | dueño finca       | Ejecutar análisis (sincrónico)       |
| GET    | `/results/{analysis_id}`          | 🔒     | dueño             | Resultado detallado                  |
| GET    | `/results/{analysis_id}/png`      | 🔒     | dueño             | PNG del resultado                    |
| GET    | `/reports/{analysis_id}/download` | 🔒     | dueño             | Descargar PDF                        |
| GET    | `/alerts`                         | 🔒     | cualquiera        | Listar mis alertas                   |
| GET    | `/alerts/unread-count`            | 🔒     | cualquiera        | Contar no leídas                     |
| PUT    | `/alerts/{id}/read`               | 🔒     | dueño             | Marcar leída                         |
| GET    | `/prices/market-prices`           | 🔒     | cualquiera        | Último precio por producto           |
| GET    | `/prices/market-prices/provenance`| 🔒     | cualquiera        | Resumen de provenancia               |
| GET    | `/prices/market-prices/history/{producto}` | 🔒 | cualquiera | Histórico de un producto       |
| GET    | `/notifications/status`           | público| -                 | Estado SMTP/Twilio                   |
| POST   | `/notifications/notify-test`      | 🔒     | cualquiera        | Probar envío                         |
| GET    | `/audit`                          | 🔒 🔐  | extensionista+    | Listar audit log                     |
| GET    | `/audit/actions`                  | 🔒 🔐  | extensionista+    | Acciones únicas                      |
| GET    | `/catalog/crops`                  | público| -                 | Catálogo de cultivos                 |
| GET    | `/catalog/geofence`               | público| -                 | Geofence                             |
| GET    | `/catalog/raster`                 | público| -                 | Config de rasters                    |
| GET    | `/catalog/all`                    | público| -                 | Los tres anteriores                  |

---

## 10. Modelo de honestidad / provenancia de datos

> **Trazabilidad MVP**: SembrarIA está construido con datos **DEMO** (sintéticos).
> La UI debe ser honesta sobre esto. El backend expone banderas para que la UI
> pueda mostrar banners apropiados.

### Banderas expuestas por la API

| Campo              | Dónde aparece                           | Significado                                              |
|--------------------|-----------------------------------------|----------------------------------------------------------|
| `is_synthetic`     | `alerts`, `market_prices`               | `true` = dato generado por seed/script, NO real          |
| `data_provenance`  | `GET /prices/market-prices/provenance`  | `synthetic` \| `real` \| `mixed` \| `empty`              |
| `mode`             | `GET /notifications/status`            | `mock` \| `live` \| `mixed` — si emails/SMS son reales   |
| `synthetic`        | `results.raster_inputs[].synthetic`     | `true` = el raster usado es demo                         |
| `model_version`    | `results.model_version`                 | versión del código que produjo el resultado              |

### Recomendaciones de UI

1. **Banner de provenancia global**: si `data_provenance="synthetic"`, mostrar
   un banner amarillo en la parte superior: *"Estás viendo datos DEMO.
   No usar para decisiones reales de mercado."*

2. **Banner de notificaciones**: si `notifications.mode="mock"`, mostrar un
   banner discreto: *"Las alertas por email/SMS están en modo demo (no
   llegan al usuario)."*

3. **Tags individuales**: en cada card de alerta/precio, un pequeño tag
   "DEMO" si `is_synthetic=true`.

4. **Información del modelo**: en la vista de resultados, mostrar
   `model_version` y `model_algorithm` para que el usuario vea con qué
   versión del algoritmo se hizo el análisis.

5. **NO esconder el origen**: cuando se conecten scrapers reales, los
   nuevos registros deben insertarse con `is_synthetic=false` y
   `source_url` apuntando a la fuente oficial.

---

## 11. Manejo de errores

El backend usa **HTTP estándar**. Los errores devuelven JSON con `detail`:

```json
{ "detail": "Email o contrasena incorrectos" }
```

| Código | Significado en este backend              | Cuándo lo ves                              |
|--------|------------------------------------------|--------------------------------------------|
| 200    | OK                                       | Respuesta exitosa                          |
| 201    | Created                                  | POST exitoso (registro, finca, etc.)       |
| 204    | No Content                               | DELETE exitoso                             |
| 400    | Bad Request                              | Validación falló (ej: email duplicado, cultivo inválido, polígono fuera de Caquetá) |
| 401    | Unauthorized                             | Token inválido o expirado                  |
| 403    | Forbidden                                | No eres dueño del recurso, o rol insuficiente (audit) |
| 404    | Not Found                                | Recurso no existe                          |
| 422    | Unprocessable Entity                     | Validación de Pydantic falló (tipo de dato, schema) |
| 429    | Too Many Requests                        | Rate limit en /auth/login                  |
| 500    | Internal Server Error                    | Error inesperado (ej: raster no disponible) |

### Estrategia recomendada en el frontend

```javascript
async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("access_token");
  const res = await fetch(`http://localhost:8001/api/v1${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { "Authorization": `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  if (res.status === 401) {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
    throw new Error("Sesión expirada");
  }
  if (res.status === 429) {
    throw new Error("Demasiadas solicitudes. Espera un momento.");
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Error ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}
```

---

## 12. Probar la integración end-to-end

### 12.1 Con cURL (rápido, sin frontend)

```bash
# 1. Health check
curl http://localhost:8001/api/v1/health

# 2. Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"productor@sembraria.demo","password":"sembraria2026"}'

# Guardar el token
TOKEN="<access_token de la respuesta>"

# 3. Ver mi usuario
curl http://localhost:8001/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 4. Listar mis fincas
curl http://localhost:8001/api/v1/farms \
  -H "Authorization: Bearer $TOKEN"

# 5. Ejecutar un análisis
curl -X POST http://localhost:8001/api/v1/analysis/farms/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cultivo":"cacao"}'

# 6. Ver el PNG del resultado
curl http://localhost:8001/api/v1/results/<analysis_id>/png \
  -H "Authorization: Bearer $TOKEN" \
  -o resultado.png

# 7. Ver alertas
curl http://localhost:8001/api/v1/alerts \
  -H "Authorization: Bearer $TOKEN"

# 8. Ver precios
curl http://localhost:8001/api/v1/prices/market-prices \
  -H "Authorization: Bearer $TOKEN"
```

### 12.2 Con el navegador (Swagger UI)

Si el backend está corriendo, abre:
```
http://localhost:8001/docs
```

Ahí puedes probar **todos** los endpoints desde el navegador, hacer login
con "Authorize" en la esquina superior derecha, y ver request/response.

### 12.3 Con el frontend

```bash
# 1. Backend arriba en puerto 8001
# 2. Frontend arriba en puerto 5173
# 3. Abrir http://localhost:5173
# 4. Login con productor@sembraria.demo / sembraria2026
# 5. Navegar al mapa → ver la finca demo
# 6. Click en "Analizar" → seleccionar "cacao"
# 7. Esperar ~2s → ver resultado con PNG, % de aptitud, hectáreas
# 8. Ir a "Alertas" → ver 3 alertas demo
# 9. Ir a "Precios" → ver precios mock con banner "DEMO"
```

---

## 13. Problemas comunes (pitfalls)

### 13.1 "CORS error" en el navegador
**Síntoma**: la consola del navegador dice *"Access to fetch has been blocked by CORS policy"*.

**Causa**: el frontend está en un origen que no está en `CORS_ORIGINS` del backend.

**Solución**: edita `.env` en la raíz del backend y agrega tu origen:
```bash
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000
```
Reinicia el backend.

### 13.2 "401 Unauthorized" apenas cargo la página
**Síntoma**: la app carga pero todas las requests fallan con 401.

**Causa**: el token no se está enviando o está expirado.

**Solución**:
- Verifica que guardas el `access_token` después del login (en
  `localStorage`, `sessionStorage` o estado en memoria).
- Verifica que envías el header `Authorization: Bearer <token>`.
- Si expiró (24h), limpia el storage y redirige a login.

### 13.3 "El polígono está fuera de Caquetá" al crear una finca
**Síntoma**: el backend devuelve 400 con ese mensaje.

**Causa**: la geometría cae fuera del bbox `[-76.3, -0.7, -73.6, 2.3]`.

**Solución**: verifica las coordenadas. Para la finca demo son
`lon: -75.62 a -75.61, lat: 1.61 a 1.62` (Florencia). Si dibujas
una finca con Leaflet, asegúrate de que la lat/lon no esté invertida
(Leaflet usa `[lat, lon]`, GeoJSON usa `[lon, lat]` — fuente clásica
de bugs).

### 13.4 "psql: command not found"
**Síntoma**: el script `setup-db.bat` no encuentra psql.

**Solución**: agrega `C:\Program Files\PostgreSQL\18\bin` al PATH de Windows
(o la versión que tengas). O usa la ruta absoluta en CMD:
```cmd
set PATH=C:\Program Files\PostgreSQL\18\bin;%PATH%
```

### 13.5 "PostGIS no está instalado" durante setup
**Síntoma**: el script 01_extensions.sql falla con `extension "postgis" is not available`.

**Solución**:
- En Windows con el instalador EDB: re-corre el instalador y al final
  selecciona "Stack Builder" → tu versión de Postgres → "PostGIS".
- En Linux: `sudo apt install postgresql-18-postgis-3` (ajusta versión).

### 13.6 El backend no arranca, dice "no se encuentra .env"
**Síntoma**: `python -m sembraria.main` falla con un error de config.

**Causa**: falta el archivo `.env` en la raíz del proyecto.

**Solución**: copia `apps/api/.env.example` a la raíz como `.env`:
```bash
copy apps\api\.env.example .env
```
Edítalo con tus credenciales (al menos `DATABASE_URL`).

### 13.7 "Cannot connect to database" 
**Síntoma**: el backend arranca pero `/health` devuelve `database.status=error`.

**Causa**: el `DATABASE_URL` no es válido, o la DB no existe.

**Solución**:
1. Verifica que la DB existe: `psql -U postgres -l | findstr sembraria`
2. Si no existe, corre `scripts\setup\setup-db.bat`
3. Verifica credenciales en `.env` (especialmente password)

### 13.8 "Address already in use" al arrancar el backend
**Síntoma**: `uvicorn` no puede bindear al puerto 8000 (u 8001).

**Causa**: otro proceso está usando el puerto.

**Solución** (Windows):
```cmd
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```
O cambia el puerto en `.env` (`API_PORT=8001`).

### 13.9 El PNG no se muestra en `<img src="...">`
**Síntoma**: el `<img>` se rompe.

**Causa**: el endpoint requiere `Authorization` header, que `<img>` no puede enviar.

**Solución**: usa `fetch` para obtener el blob:
```javascript
const res = await fetch(`${API_URL}/results/${id}/png`, {
  headers: { Authorization: `Bearer ${token}` }
});
const blob = await res.blob();
const url = URL.createObjectURL(blob);
imgElement.src = url;
// Cuando el componente se desmonte:
URL.revokeObjectURL(url);
```

### 13.10 "JWT expired" justo después de loguear
**Síntoma**: el token expira demasiado rápido.

**Solución**: edita `.env` y aumenta `JWT_EXPIRE_HOURS=24` (default) a lo que
necesites. No hay refresh tokens en el MVP.

---

## 14. Resumen rápido (cheatsheet)

```
╔══════════════════════════════════════════════════════════════════╗
║  SembrarIA — Cheatsheet para el compañero de frontend            ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  BASE URL:    http://localhost:8001/api/v1                        ║
║  FRONTEND:    http://localhost:5173                               ║
║                                                                   ║
║  DB:          postgresql://postgres:1234@localhost:5432/sembraria ║
║  USERS DEMO:  productor@sembraria.demo / sembraria2026            ║
║               cooperativa@sembraria.demo / sembraria2026          ║
║  FINCA DEMO:  aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa (Florencia)   ║
║                                                                   ║
║  AUTH:        POST /auth/login → access_token                     ║
║               Header: Authorization: Bearer <token>               ║
║               Token expira en 24h (no hay refresh)                ║
║                                                                   ║
║  FLUJO TÍPICO:                                                    ║
║    1. POST /auth/login         (público)                          ║
║    2. GET /farms               (ver fincas del usuario)           ║
║    3. POST /farms              (crear nueva con POLYGON)          ║
║    4. POST /analysis/farms/{id}/analyze  (sync, ~2s)              ║
║    5. GET /results/{analysis_id}  (PNG, criterios, resumen)       ║
║    6. GET /reports/{analysis_id}/download  (PDF)                  ║
║                                                                   ║
║  RATE LIMIT: /auth/login = 10 req/min por IP                      ║
║  RBAC: /audit requiere rol extensionista+                         ║
║  GEOMETRÍA: PostGIS POLYGON, SRID 4326, lon/lat (no lat/lon)      ║
║                                                                   ║
║  BANDERAS DE HONESTIDAD:                                          ║
║    alerts[i].is_synthetic      → muestra "DEMO" si true           ║
║    market_prices[i].is_synthetic → muestra "DEMO" si true         ║
║    /prices/.../provenance      → banner global synthetic/real    ║
║    /notifications/status.mode  → "mock" si SMTP/SMS no son reales║
║                                                                   ║
║  HEALTH: GET /api/v1/health (público) debe devolver status="ok"  ║
║  DOCS SWAGGER: http://localhost:8001/docs                         ║
║                                                                   ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Anexo A — Pasos exactos para que tu compañero levante todo en 10 minutos

```bash
# === 0. Verificar versiones ===
psql --version           # debe ser 13+
python --version         # debe ser 3.12+
node --version           # debe ser 20+ (solo si va a tocar el frontend)

# === 1. Clonar el repo (si aún no lo tiene) ===
cd C:\Users\NITRO\Desktop\Proyecto    # o donde prefiera
git clone <url-del-repo> SembraIA
cd SembraIA

# === 2. Configurar el .env raíz ===
copy apps\api\.env.example .env
# Editar .env:
#   DATABASE_URL=postgresql+psycopg2://postgres:1234@localhost:5432/sembraria
#   (dejar el resto por defecto)

# === 3. Crear la base de datos ===
scripts\setup\setup-db.bat
# (o el .sh en Linux/WSL)
# Esto: drop sembraria → create sembraria → corre 9 scripts SQL

# === 4. Backend ===
cd apps\api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m sembraria.main
# Backend en http://127.0.0.1:8001
# Swagger en http://127.0.0.1:8001/docs

# === 5. Frontend (otra terminal) ===
cd apps\web
npm install
npm run dev
# Frontend en http://localhost:5173

# === 6. Probar en el navegador ===
# Abrir http://localhost:5173
# Login: productor@sembraria.demo / sembraria2026
# Mapa → ver finca demo → Analizar → Cacao
# Esperar 2s → ver el resultado
```

Si algo falla, ir a §13 (problemas comunes).

---

## Anexo B — Dónde está cada cosa

| Quiero ver...                            | Archivo / ruta                                  |
|------------------------------------------|--------------------------------------------------|
| Lista de endpoints                       | `apps/api/sembraria/api/*.py`                   |
| Schemas Pydantic (request/response)      | `apps/api/sembraria/schemas/`                    |
| Modelos de DB                            | `apps/api/sembraria/models/`                    |
| Lógica de negocio                        | `apps/api/sembraria/services/`                  |
| Algoritmo de análisis                    | `apps/api/sembraria/services/zonal_extraction.py` |
| Configuración (.env)                     | `.env` en la raíz                               |
| Migraciones SQL                          | `config/db/01..09_*.sql`                        |
| Catálogo de cultivos                     | `config/catalog/crops.yaml`                     |
| Geofence de Caquetá                      | `config/catalog/geofence.yaml`                  |
| Config de rasters                        | `config/catalog/raster.yaml`                    |
| Rasters de entrada                       | `data/inputs/`                                  |
| Outputs (PNG/PDF)                        | `data/outputs/`                                 |
| Tests                                    | `apps/api/tests/`                               |
| GitHub Actions CI                        | `.github/workflows/`                            |
| Docker                                   | `Dockerfile`, `docker-compose.yml`              |
| Scripts de setup/dev                     | `scripts/setup/`, `scripts/dev/`, `scripts/test/` |

---

**Última actualización**: 2026-06-03
**Backend version**: 1.0.0
**Contacto**: noreply@sembriaia.udla.edu.co
