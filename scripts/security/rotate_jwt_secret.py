#!/usr/bin/env python
"""
SembrarIA - Rotacion de la clave JWT.

Que hace:
  1. Lee el .env actual
  2. Genera una nueva clave JWT_SECRET aleatoria (64 bytes url-safe)
  3. Mueve la clave actual a PREVIOUS_JWT_SECRET (para que los tokens
     en vuelo sigan siendo validos durante el periodo de gracia)
  4. Incrementa el identificador de clave (v1 -> v2, etc.)
  5. Escribe de vuelta al .env con timestamp de rotacion
  6. (Opcional) Registra el evento en el audit log

Uso:
    # Rotacion interactiva (pide confirmacion)
    python scripts/security/rotate_jwt_secret.py

    # Rotacion sin confirmacion (para CI/CD)
    python scripts/security/rotate_jwt_secret.py --yes

    # Sin escribir al audit log (si la DB no esta accesible)
    python scripts/security/rotate_jwt_secret.py --no-audit

    # Especificar duracion del periodo de gracia (segundos)
    python scripts/security/rotate_jwt_secret.py --grace 43200

IMPORTANTE:
  - Todos los usuarios que tengan tokens activos seguiran autenticados
    durante `jwt_grace_seconds` segundos. Pasado ese plazo, deberan
    volver a hacer login.
  - Si queres INVALIDAR todos los tokens inmediatamente, pasa
    --grace 0 (la clave anterior se descarta al instante).
  - Este script NO reinicia el backend. Despues de rotar, reinicia
    el proceso para que cargue la nueva clave.
"""
import argparse
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT_DIR / ".env"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Rota la clave JWT de SembrarIA y actualiza .env"
    )
    p.add_argument(
        "--yes",
        action="store_true",
        help="No pedir confirmacion interactiva",
    )
    p.add_argument(
        "--no-audit",
        action="store_true",
        help="No escribir en el audit log (usar si la DB no esta accesible)",
    )
    p.add_argument(
        "--grace",
        type=int,
        default=None,
        help="Periodo de gracia en segundos (default: leer de .env o 86400)",
    )
    p.add_argument(
        "--env-file",
        type=Path,
        default=ENV_FILE,
        help=f"Ruta al .env (default: {ENV_FILE})",
    )
    return p.parse_args()


def read_env(env_file: Path) -> dict[str, str]:
    """Lee el .env como dict (preserva comentarios y lineas vacias)."""
    if not env_file.exists():
        print(f"ERROR: no se encontro {env_file}", file=sys.stderr)
        sys.exit(1)
    env = {}
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def write_env(env_file: Path, env: dict[str, str]) -> None:
    """Sobrescribe el .env manteniendo comentarios y formato."""
    lines = env_file.read_text(encoding="utf-8").splitlines()
    new_lines = []
    seen_keys = set()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            new_lines.append(line)
            continue
        key = line.partition("=")[0].strip()
        if key in env:
            new_lines.append(f"{key}={env[key]}")
            seen_keys.add(key)
        else:
            new_lines.append(line)
    # Agregar claves nuevas al final
    for key, value in env.items():
        if key not in seen_keys:
            new_lines.append(f"{key}={value}")
    env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def bump_key_id(current: str) -> str:
    """v1 -> v2, vN -> v(N+1). Si no matchea el patron, devuelve v_next."""
    m = re.match(r"^v(\d+)$", current)
    if m:
        return f"v{int(m.group(1)) + 1}"
    return "v_next"


def rotate(args: argparse.Namespace) -> int:
    env_file: Path = args.env_file
    env = read_env(env_file)

    current_secret = env.get("JWT_SECRET", "")
    if not current_secret:
        print(
            "ERROR: no se encontro JWT_SECRET en el .env",
            file=sys.stderr,
        )
        return 1
    if current_secret == "change-me-in-production":
        print(
            "ERROR: la clave JWT_SECRET actual es la del default de desarrollo.\n"
            "       Genera una nueva primero con:\n"
            '         python -c "import secrets; print(secrets.token_urlsafe(64))"\n'
            "       y pegala en .env antes de rotar.",
            file=sys.stderr,
        )
        return 1

    current_kid = env.get("JWT_KEY_ID", "v1")
    new_kid = bump_key_id(current_kid)
    new_secret = secrets.token_urlsafe(64)
    rotated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    grace = args.grace
    if grace is None:
        try:
            grace = int(env.get("JWT_GRACE_SECONDS", "86400"))
        except ValueError:
            grace = 86400

    print("=" * 60)
    print("Rotacion de clave JWT - SembrarIA")
    print("=" * 60)
    print(f"Archivo .env:    {env_file}")
    print(f"Kid actual:      {current_kid}")
    print(f"Kid nuevo:       {new_kid}")
    print(f"Rotado a:        {rotated_at}")
    print(f"Periodo gracia:  {grace} segundos ({grace / 3600:.1f} horas)")
    print(f"Nuevo secreto:   {new_secret[:12]}...{new_secret[-8:]} ({len(new_secret)} chars)")
    print()

    if not args.yes:
        resp = input("Confirmar rotacion? [s/N]: ").strip().lower()
        if resp not in ("s", "si", "y", "yes"):
            print("Cancelado.")
            return 0

    # Mover la actual a la anterior
    env["PREVIOUS_JWT_SECRET"] = current_secret
    env["PREVIOUS_JWT_KEY_ID"] = current_kid
    env["JWT_SECRET"] = new_secret
    env["JWT_KEY_ID"] = new_kid
    env["JWT_ROTATED_AT"] = rotated_at
    env["JWT_GRACE_SECONDS"] = str(grace)

    write_env(env_file, env)
    print(f"OK: {env_file} actualizado")
    print()
    print("Proximos pasos:")
    print("  1. Reiniciar el backend para que cargue la nueva clave:")
    print("       (en PowerShell) Restart-Service uvicorn_sembraria")
    print("       (o matar el proceso y volver a lanzar uvicorn)")
    print("  2. Verificar el endpoint /api/v1/health")
    print("  3. (Opcional) Esperar el periodo de gracia antes de eliminar")
    print("     PREVIOUS_JWT_SECRET del .env para invalidar tokens viejos.")

    # Audit log
    if not args.no_audit:
        try:
            sys.path.insert(0, str(ROOT_DIR / "apps" / "api"))
            from sembraria.database import SessionLocal
            from sembraria.services.audit_service import log_event
            from sembraria.config import get_settings

            settings = get_settings()
            with SessionLocal() as db:
                entry = log_event(
                    db,
                    user_id=None,
                    action="jwt_secret_rotated",
                    resource="security",
                    resource_id=None,
                    request=None,
                    details={
                        "old_kid": current_kid,
                        "new_kid": new_kid,
                        "grace_seconds": grace,
                        "rotated_at": rotated_at,
                    },
                )
                if entry:
                    print(f"Audit log: registrado evento {entry.id}")
                else:
                    print(
                        "WARN: audit log no se pudo escribir (ver logs de la app)"
                    )
        except Exception as e:
            print(f"WARN: no se pudo escribir en el audit log: {e}")
            print("      La rotacion del .env fue exitosa de todas formas.")

    return 0


def main() -> int:
    args = parse_args()
    return rotate(args)


if __name__ == "__main__":
    sys.exit(main())
