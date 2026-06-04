"""
Auth endpoints: register, login, me.
JWT propio con bcrypt.
Todos los eventos de auth quedan registrados en el audit log.
El endpoint /login esta protegido por rate limiting (slowapi) para
prevenir ataques de fuerza bruta.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from sembraria.database import get_db
from sembraria.models.user import User
from sembraria.rate_limit import _login_key, limiter, login_limit
from sembraria.schemas.user import Token, UserCreate, UserLogin, UserOut
from sembraria.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from sembraria.services.audit_service import log_event

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Dependency: extrae el usuario actual desde el JWT."""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token invalido")

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token invalido")

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    return user


@router.post("/register", response_model=Token, status_code=201)
async def register(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Registra un nuevo usuario."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    user = User(
        email=payload.email,
        phone=payload.phone,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        organization=payload.organization,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_event(
        db,
        user_id=str(user.id),
        action="register",
        resource="user",
        resource_id=str(user.id),
        request=request,
        details={"email": user.email, "role": user.role.value},
    )

    token = create_access_token(
        subject=str(user.id), extra_claims={"role": user.role.value}
    )
    return Token(
        access_token=token,
        user=UserOut.model_validate(user),
    )


@router.post("/login", response_model=Token)
@limiter.limit(login_limit, key_func=_login_key)
async def login(
    payload: UserLogin,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """Inicia sesion y devuelve JWT."""
    user = db.query(User).filter(User.email == payload.email).first()
    password_ok = bool(user and verify_password(payload.password, user.hashed_password))
    if not password_ok:
        log_event(
            db,
            user_id=None,
            action="login_failed",
            resource="auth",
            request=request,
            details={"email": payload.email, "reason": "invalid_credentials"},
        )
        raise HTTPException(status_code=401, detail="Email o contrasena incorrectos")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    log_event(
        db,
        user_id=str(user.id),
        action="login",
        resource="user",
        resource_id=str(user.id),
        request=request,
        details={"email": user.email},
    )

    token = create_access_token(
        subject=str(user.id), extra_claims={"role": user.role.value}
    )
    return Token(
        access_token=token,
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    """Devuelve el usuario actual (requiere JWT)."""
    return current_user
