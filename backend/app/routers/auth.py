import uuid as _uuid

import jwt
from fastapi import APIRouter, Cookie, Depends, Response, status
from sqlmodel import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.usuario import Usuario
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    ChangePasswordRequest,
    MessageResponse,
)
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    set_access_cookie,
    set_refresh_cookie,
    clear_auth_cookies,
    verify_password,
    hash_password,
    update_last_access,
)
from app.utils.errors import NIAException

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, body.email, body.password)
    if not user:
        raise NIAException(
            code="INVALID_CREDENTIALS",
            message="Email o contraseña incorrectos",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    set_access_cookie(response, access_token)
    set_refresh_cookie(response, refresh_token)

    update_last_access(db, user)

    return LoginResponse(
        user=TokenResponse(
            id=str(user.id),
            nombre=user.nombre,
            email=user.email,
            rol=user.rol,
        )
    )


@router.post("/refresh")
def refresh_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        raise NIAException(
            code="AUTH_REFRESH_FAILED",
            message="No refresh token provided",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
        if not user_id:
            raise NIAException(
                code="AUTH_INVALID_TOKEN",
                message="Invalid refresh token",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
    except jwt.ExpiredSignatureError:
        raise NIAException(
            code="AUTH_TOKEN_EXPIRED",
            message="Refresh token expired",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    except jwt.InvalidTokenError:
        raise NIAException(
            code="AUTH_INVALID_TOKEN",
            message="Invalid refresh token",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        user_uuid = _uuid.UUID(user_id)
    except ValueError:
        raise NIAException(
            code="AUTH_INVALID_TOKEN",
            message="Invalid refresh token",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user = db.query(Usuario).filter(Usuario.id == user_uuid).first()
    if not user or not user.activo:
        raise NIAException(
            code="AUTH_INVALID_TOKEN",
            message="Invalid refresh token",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    new_access_token = create_access_token(str(user.id))
    set_access_cookie(response, new_access_token)

    return {"message": "Token refreshed"}


@router.post("/logout", response_model=MessageResponse)
def logout(response: Response):
    clear_auth_cookies(response)
    return MessageResponse(message="Logged out")


@router.get("/me", response_model=TokenResponse)
def me(user: Usuario = Depends(get_current_user)):
    return TokenResponse(
        id=str(user.id),
        nombre=user.nombre,
        email=user.email,
        rol=user.rol,
    )


@router.put("/change-password", response_model=MessageResponse)
def change_password(
    body: ChangePasswordRequest,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(body.current_password, user.password_hash):
        raise NIAException(
            code="INVALID_CREDENTIALS",
            message="Current password is incorrect",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if len(body.new_password) < 8:
        raise NIAException(
            code="VAL_PASSWORD_TOO_SHORT",
            message="Password must be at least 8 characters",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    user.password_hash = hash_password(body.new_password)
    db.add(user)
    db.commit()

    return MessageResponse(message="Password updated")
