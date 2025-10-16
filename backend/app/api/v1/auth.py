"""
Endpoints de autenticacion (Login, Logout, Get Current User).
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import Token, LoginRequest
from app.schemas.user import User as UserSchema


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token, summary="Login de usuario")
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login de usuario con email y password.

    Retorna un token JWT que debe ser usado en requests subsiguientes
    en el header Authorization: Bearer <token>

    Args:
        login_data: Email y password del usuario
        db: Sesion de base de datos

    Returns:
        Token: access_token y token_type

    Raises:
        HTTPException 401: Si las credenciales son incorrectas
    """
    # Buscar usuario por email
    user = db.query(User).filter(User.email == login_data.email).first()

    # Verificar que el usuario existe y la password es correcta
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar que el usuario este activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )

    # Crear token JWT
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )

    # Actualizar last_login_at
    user.last_login_at = datetime.utcnow()
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserSchema, summary="Obtener usuario actual")
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene informacion del usuario actualmente autenticado.

    Requiere token JWT valido en el header Authorization.

    Args:
        current_user: Usuario actual (de dependencia)

    Returns:
        UserSchema: Informacion del usuario
    """
    return current_user


@router.post("/logout", summary="Logout de usuario")
def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout del usuario actual.

    NOTA: En esta implementacion simple, el logout es del lado del cliente
    (eliminar el token). En produccion, se podria implementar una blacklist
    de tokens en Redis.

    Args:
        current_user: Usuario actual

    Returns:
        dict: Mensaje de exito
    """
    return {"message": "Logout exitoso"}
