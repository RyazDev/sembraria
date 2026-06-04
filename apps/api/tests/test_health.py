"""
Tests del endpoint /health y readiness/liveness probes.
"""


def test_health_returns_200(client):
    """/health responde 200."""
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200


def test_health_payload_has_required_fields(client):
    """/health incluye status, app, database, rasters."""
    resp = client.get("/api/v1/health")
    data = resp.json()
    assert "status" in data
    assert data["status"] in ("ok", "degraded", "error")
    assert "app" in data
    assert "name" in data["app"]
    assert "version" in data["app"]
    assert "database" in data
    assert "rasters" in data
    assert "disk" in data
    assert "timestamp" in data


def test_health_db_section_reports_postgres_and_postgis(client):
    """/health reporta version de Postgres y PostGIS."""
    resp = client.get("/api/v1/health")
    db = resp.json()["database"]
    assert "version" in db
    assert "postgis_version" in db
    assert "migrations_applied" in db
    assert db["version"] is not None
    assert db["postgis_version"] is not None
    assert db["migrations_applied"] >= 1


def test_health_rasters_lists_all_inputs(client):
    """/health lista los 6 rasters sinteticos esperados."""
    resp = client.get("/api/v1/health")
    rasters = resp.json()["rasters"]
    assert isinstance(rasters, dict)
    expected = [
        "aptitud_CACAO.tif",
        "aptitud_PLATANO.tif",
        "aptitud_YUCA.tif",
        "clasificacion_5clases.tif",
        "sintesis_mejor_cultivo.tif",
        "stack_54features.tif",
    ]
    for name in expected:
        assert name in rasters, f"Falta raster {name} en /health"
        r = rasters[name]
        assert "status" in r
        assert r["status"] == "ok", f"raster {name} no esta ok: {r}"


def test_health_live_returns_200(client):
    """Liveness probe responde 200 con {alive: true}."""
    resp = client.get("/api/v1/health/live")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("alive") is True


def test_health_ready_returns_db_status(client):
    """Readiness probe devuelve estado de la DB."""
    resp = client.get("/api/v1/health/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert "ready" in data
    assert "database" in data
    # En este MVP la DB siempre esta up
    assert data["ready"] is True
    assert data["database"] == "ok"
