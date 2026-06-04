"""
Tests del modulo de seguridad: JWT, bcrypt, rotacion de claves.
"""
import base64
import json
from datetime import datetime, timedelta, timezone

import jose.jwt as jwt
import pytest

from sembraria.config import get_settings
from sembraria.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
    is_jwt_recently_rotated,
)


def test_password_hash_and_verify():
    """bcrypt hash + verify roundtrip."""
    plain = "supersecret123"
    hashed = hash_password(plain)
    assert hashed != plain
    assert hashed.startswith(("$2a$", "$2b$", "$2y$"))
    assert verify_password(plain, hashed)
    assert not verify_password("wrong", hashed)


def test_password_truncation_at_72_bytes():
    """Bcrypt solo acepta hasta 72 bytes. Las contrasenas largas se truncan.

    Nota: bcrypt trunca SILENCIOSAMENTE al hashear y al verificar, asi que
    una contrasena de 100 'x' y una de 72 'x' dan el mismo hash y validan
    entre si. Lo importante es que NO falla con contrasenas largas.
    """
    long_pw = "x" * 100
    hashed = hash_password(long_pw)
    # La version corta (72 x) valida porque bcrypt trunco al hashear
    assert verify_password("x" * 72, hashed)
    # NO debe explotar con contrasenas largas
    assert verify_password("x" * 100, hashed)
    # Pero si es diferente en los primeros 72 bytes, NO valida
    assert not verify_password("y" * 72, hashed)


def test_jwt_encode_decode_roundtrip():
    """Token creado se puede decodificar."""
    token = create_access_token("user-123", extra_claims={"role": "productor"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"
    assert payload["role"] == "productor"
    assert "exp" in payload
    assert "iat" in payload
    assert "kid" in payload


def test_jwt_includes_kid_in_payload():
    """El token JWT incluye `kid` (key id) en el payload."""
    token = create_access_token("user-123")
    payload = decode_access_token(token)
    assert "kid" in payload
    settings = get_settings()
    assert payload["kid"] == settings.jwt_key_id


def test_jwt_decode_invalid_returns_none():
    """Token con firma invalida devuelve None."""
    fake_token = jwt.encode(
        {"sub": "user-123", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        "this-is-not-the-real-key",
        algorithm="HS256",
    )
    payload = decode_access_token(fake_token)
    assert payload is None


def test_jwt_decode_garbage_returns_none():
    """String basura devuelve None (no exception)."""
    assert decode_access_token("not.a.token") is None
    assert decode_access_token("") is None
    assert decode_access_token("a.b.c") is None


def test_jwt_decode_expired_returns_none():
    """Token expirado devuelve None."""
    expired = jwt.encode(
        {
            "sub": "user-123",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=10),
            "kid": "v1",
        },
        get_settings().jwt_secret,
        algorithm="HS256",
    )
    payload = decode_access_token(expired)
    assert payload is None


def test_jwt_grace_period_accepts_previous_key():
    """Si hay previous_jwt_secret configurado, un token firmado con esa
    clave tambien es aceptado durante el periodo de gracia."""
    settings = get_settings()
    if not settings.previous_jwt_secret:
        pytest.skip("No hay previous_jwt_secret configurada (no se ha rotado)")
    old_token = jwt.encode(
        {
            "sub": "user-old",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "kid": settings.previous_jwt_key_id or "v_old",
        },
        settings.previous_jwt_secret,
        algorithm="HS256",
    )
    payload = decode_access_token(old_token)
    assert payload is not None
    assert payload["sub"] == "user-old"
