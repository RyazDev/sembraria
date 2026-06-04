# Quickstart — Arrancar SembrarIA en 30 segundos

> **TL;DR**: Abre VS Code, dos terminales, corre los dos comandos de abajo. Listo.

---

## Prerrequisitos (ya los tienes instalados)

- Python 3.12+ (con venv `apps/api/.venv/`)
- Node.js 20+ (con `node_modules/` en `apps/web/`)
- PostgreSQL 18 + PostGIS 3.6 corriendo en `localhost:5432`
- DB `sembraria` ya creada con las 9 migraciones SQL aplicadas
- Archivo `.env` en la raíz con `DATABASE_URL=postgresql+psycopg2://postgres:1234@localhost:5432/sembraria`

---

## Paso 1 — Abrir VS Code en el proyecto

```
File → Open Folder → C:\Users\NITRO\Desktop\Proyecto\SembraIA
```

Abre la terminal integrada: `Ctrl+ñ`

---

## Paso 2 — Arrancar el BACKEND (Terminal 1)

Copia y pega **tal cual**:

```bash
cd "C:\Users\NITRO\Desktop\Proyecto\SembraIA\apps\api" && .venv\Scripts\activate && python -m sembraria.main
```

Verás algo como:

```
Inicializando base de datos SembrarIA...
Base de datos lista. 9 migraciones aplicadas.
INFO:     Uvicorn running on http://127.0.0.1:8001
```

✅ **Backend arriba en puerto 8001**

> **NO es `run dev`** — eso es para npm/Node. El backend es Python con uvicorn.

---

## Paso 3 — Arrancar el FRONTEND (Terminal 2)

Click en el `+` de la barra de terminales para abrir una **segunda terminal**, luego:

```bash
cd "C:\Users\NITRO\Desktop\Proyecto\SembraIA\apps\web" && npm run dev
```

Verás algo como:

```
  VITE v5.x.x  ready in 312 ms

  ➜  Local:   http://localhost:5173/
```

✅ **Frontend arriba en puerto 5173**

> **ESTE sí es `npm run dev`** — Vite usa ese comando.

---

## Paso 4 — Probar que todo está conectado

Abre en el navegador:

| URL | Qué deberías ver |
|---|---|
| <http://127.0.0.1:8001/api/v1/health> | JSON con `"status": "ok"` |
| <http://127.0.0.1:8001/docs> | Swagger UI con los 31 endpoints |
| <http://localhost:5173> | Landing page de SembrarIA |

Si los tres cargan, **frontend y backend están conectados correctamente**.

---

## Login de prueba (en el frontend)

| Email | Password | Rol |
|---|---|---|
| `productor@sembraria.demo` | `sembraria2026` | productor |
| `cooperativa@sembraria.demo` | `sembraria2026` | cooperativa |

---

## Apagar todo

En cada terminal: `Ctrl+C`

Si quedó algo colgado, fuerza el cierre:

```bash
scripts\dev\stop-all.bat
```

---

## Resumen — los 2 comandos

| Servicio | Comando (copia y pega) | Puerto |
|---|---|---|
| **Backend** | `cd "C:\Users\NITRO\Desktop\Proyecto\SembraIA\apps\api" && .venv\Scripts\activate && python -m sembraria.main` | 8001 |
| **Frontend** | `cd "C:\Users\NITRO\Desktop\Proyecto\SembraIA\apps\web" && npm run dev` | 5173 |

---

## Si algo falla

### "python no se reconoce"
Usa la ruta absoluta al Python del venv:
```bash
"C:\Users\NITRO\Desktop\Proyecto\SembraIA\apps\api\.venv\Scripts\python.exe" -m sembraria.main
```

### "No module named 'fastapi'"
El venv no tiene las deps:
```bash
cd "C:\Users\NITRO\Desktop\Proyecto\SembraIA\apps\api"
.venv\Scripts\activate
pip install -r requirements.txt
```

### "address already in use" en 8001
```bash
scripts\dev\stop-all.bat
```

### "npm no se reconoce"
Reinstala Node.js marcando "Add to PATH", luego cierra y reabre VS Code.

### "database 'sembraria' does not exist"
```bash
scripts\setup\setup-db.bat
```

### Frontend muestra "Network Error" en login
El backend no está corriendo. Verifica la Terminal 1.

---

**Última actualización**: 2026-06-04
**Backend version**: 1.0.0
**Frontend version**: 1.0.0
