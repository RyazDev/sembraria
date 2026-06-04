"""
Conftest: fixtures compartidos para tests.

Cada test corre con su propia sesion de DB para no contaminar
los datos del dev/prod. La DB usada es la misma del .env
(postgresql://postgres:1234@localhost:5432/sembraria_tests) si
existe; si no, usa la de desarrollo.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os

# Permite apuntar a una DB de tests via env var (CI).
os.environ.setdefault("TESTING", "1")

import pytest
from fastapi.testclient import TestClient

from sembraria.main import app
from sembraria.rate_limit import limiter


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Limpia el limiter de slowapi antes de cada test.

    El limiter usa almacenamiento en memoria. Si un test dispara muchos
    logins, los siguientes tests fallan con 429. Esta fixture resetea
    el storage para que cada test parta de un contador limpio.
    """
    yield
    try:
        limiter.reset()
    except Exception:
        pass


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Cliente de testing para FastAPI. Una sola instancia para toda la sesion."""
    return TestClient(app)


@pytest.fixture
def auth_token(client) -> str:
    """Devuelve un JWT real haciendo login con el usuario seed productor."""
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "productor@sembraria.demo", "password": "sembraria2026"},
    )
    assert resp.status_code == 200, f"Login fallo: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture
def cooperativa_token(client) -> str:
    """Devuelve un JWT real del usuario cooperativa (puede ver audit)."""
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "cooperativa@sembraria.demo", "password": "sembraria2026"},
    )
    assert resp.status_code == 200, f"Login cooperativa fallo: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token) -> dict:
    """Headers Authorization con un JWT real del usuario productor."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def cooperativa_headers(cooperativa_token) -> dict:
    """Headers Authorization con un JWT real del usuario cooperativa."""
    return {"Authorization": f"Bearer {cooperativa_token}"}


@pytest.fixture
def demo_farm_id() -> str:
    """UUID de la finca seed (Finca La Esperanza)."""
    return "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"


@pytest.fixture
def demo_farm_polygon() -> dict:
    """Poligono WKT valido de una finca pequena (1 ha aprox)."""
    return {
        "type": "Polygon",
        "coordinates": [[
            [-75.62, 1.61], [-75.6199, 1.61], [-75.6199, 1.6101], [-75.62, 1.6101],
            [-75.62, 1.61],
        ]],
    }
