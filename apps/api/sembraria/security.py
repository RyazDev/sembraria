"""
SembrarIA - Seguridad: JWT + bcrypt password hashing.

Soporta rotacion de claves con periodo de gracia:
  - Los tokens NUEVOS se firman con `jwt_secret` (kid=jwt_key_id).
  - Los tokens VIEJOS firmados con `previous_jwt_secret` (kid=previous_jwt_key_id)
    siguen siendo validos durante `jwt_grace_seconds` segundos.
  - Pasado ese plazo, los tokens viejos quedan invalidos y los usuarios
    deben volver a hacer login.

Para rotar la clave, ejecutar:
    python scripts/security/rotate_jwt_secret.py

NOTA: Usamos la libreria bcrypt directamente (no passlib) porque
passlib 1.7.4 (ultima version, 2020) es incompatible con bcrypt >= 5.0.
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

import bcrypt
from jose import JWTError, jwt

from sembraria.config import get_settings

settings = get_settings()

# Parametros de bcrypt
_BCRYPT_ROUNDS = 12
_BCRYPT_MAX_BYTES = 72  # limite de bcrypt


def _truncate_password(password: str) -> bytes:
    """Bcrypt solo acepta hasta 72 bytes. Truncamos silenciosamente."""
    encoded = password.encode("utf-8")
    return encoded[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    """Hashea una contrasena con bcrypt (12 rounds)."""
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    return bcrypt.hashpw(_truncate_password(password), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica una contrasena contra su hash. Acepta hashes $2a$, $2b$, $2y$."""
    try:
        return bcrypt.checkpw(_truncate_password(plain), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _signing_keys() -> List[Tuple[str, str]]:
    """
    Lista de (clave, kid) en orden de prioridad. El primero es el activo
    (con el que se FIRMA), el segundo es el de gracia (solo VERIFICA).
    """
    keys = [(settings.jwt_secret, settings.jwt_key_id)]
    if settings.previous_jwt_secret and settings.previous_jwt_key_id:
        # Solo mantenemos la clave anterior si estamos dentro del periodo
        # de gracia. Si ya expiro, la ignoramos.
        if settings.jwt_rotated_at:
            try:
                rotated_at = datetime.fromisoformat(settings.jwt_rotated_at)
                if datetime.now(timezone.utc) - rotated_at > timedelta(
                    seconds=settings.jwt_grace_seconds
                ):
                    return keys
            except ValueError:
                pass
        keys.append((settings.previous_jwt_secret, settings.previous_jwt_key_id))
    return keys


def create_access_token(
    subject: str,
    extra_claims: Optional[dict] = None,
    expires_minutes: Optional[int] = None,
) -> str:
    """Crea un JWT con subject (user_id), kid (key id) y expiracion."""
    expires = expires_minutes or settings.access_token_expire_minutes
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=expires)
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(subject),
        "exp": expire_at,
        "iat": now,
        "nbf": now,
        "kid": settings.jwt_key_id,
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica un JWT probando primero la clave activa y luego la anterior
    (si existe y no expiro el periodo de gracia).
    Devuelve None si el token no se puede verificar con ninguna clave.
    """
    for key, _kid in _signing_keys():
        try:
            return jwt.decode(
                token, key, algorithms=[settings.jwt_algorithm]
            )
        except JWTError:
            continue
    return None


def is_jwt_recently_rotated() -> bool:
    """True si la clave actual se roto en los ultimos N segundos (para auditoria)."""
    if not settings.jwt_rotated_at:
        return False
    try:
        rotated_at = datetime.fromisoformat(settings.jwt_rotated_at)
        return (
            datetime.now(timezone.utc) - rotated_at
            < timedelta(seconds=settings.jwt_grace_seconds)
        )
    except ValueError:
        return False
