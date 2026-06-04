"""
Smoke tests para los endpoints criticos.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_health(client):
    """El endpoint /health responde."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "app" in data


def test_catalog_crops(client):
    """El catalogo de cultivos responde."""
    response = client.get("/api/v1/catalog/crops")
    assert response.status_code == 200
    data = response.json()
    assert "crops" in data
    assert len(data["crops"]) >= 3  # Cacao, Platano, Yuca


def test_root(client):
    """El endpoint raiz responde."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "SembrarIA"


def test_protected_requires_auth(client):
    """Endpoints protegidos requieren token."""
    response = client.get("/api/v1/farms")
    assert response.status_code == 401
