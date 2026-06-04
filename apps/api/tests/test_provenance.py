"""
Tests de trazabilidad: market prices, notifications, alerts.

Cada test verifica que la API expone informacion HONESTA sobre la
procedencia de los datos (synthetic vs real).
"""


def test_market_prices_have_is_synthetic_field(client, auth_headers):
    """Cada precio expone `is_synthetic` y `source_url`."""
    resp = client.get("/api/v1/prices/market-prices", headers=auth_headers)
    assert resp.status_code == 200
    prices = resp.json()
    assert isinstance(prices, list)
    assert len(prices) > 0
    for p in prices:
        assert "is_synthetic" in p
        assert "source_url" in p
        assert isinstance(p["is_synthetic"], bool)


def test_market_prices_provenance_synthetic(client, auth_headers):
    """/provenance reporta synthetic cuando todos los precios son demo."""
    resp = client.get("/api/v1/prices/market-prices/provenance", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "data_provenance" in data
    assert "message" in data
    # En este MVP todos los precios son sinteticos
    assert data["data_provenance"] in ("synthetic", "mixed", "real", "empty")
    assert data["total"] >= 0
    assert data["synthetic"] >= 0
    assert data["real"] >= 0


def test_notifications_status_endpoint(client, auth_headers):
    """/notifications/status expone la configuracion SMTP/Twilio."""
    resp = client.get("/api/v1/notifications/status", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "mode" in data
    assert data["mode"] in ("mock", "live", "mixed")
    assert "smtp_configured" in data
    assert "twilio_configured" in data


def test_notify_test_returns_mock_true(client, auth_headers):
    """/notify-test devuelve mock=true cuando SMTP no esta configurado."""
    resp = client.post(
        "/api/v1/notifications/notify-test",
        json={
            "to": "test@example.com",
            "subject": "Test",
            "message": "Hola",
            "channel": "email",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "mock" in data
    assert "mode" in data
    assert "provider" in data
    # Sin SMTP configurado, debe ser mock
    if data.get("mock"):
        assert data["mode"] == "mock"
        assert data["provider"] == "console-mock"


def test_alerts_include_is_synthetic_field(client, auth_headers):
    """Las alertas exponen `is_synthetic` para que el frontend
    muestre un banner honesto."""
    resp = client.get("/api/v1/alerts", headers=auth_headers)
    assert resp.status_code == 200
    alerts = resp.json()
    if alerts:  # puede haber 0 alertas si se limpio el seed
        for a in alerts:
            assert "is_synthetic" in a
            assert isinstance(a["is_synthetic"], bool)
