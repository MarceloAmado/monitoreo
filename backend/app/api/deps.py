"""
Dependencias de FastAPI para los endpoints.

Incluye:
- get_db: Dependencia para obtener sesion de base de datos
- get_current_user: Dependencia para obtener usuario autenticado
- get_current_active_user: Usuario autenticado y activo
- require_admin: Requiere que el usuario sea admin
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.auth import TokenData


# Security scheme para JWT
security = HTTPBearer()


def get_db() -> Generator:
    """
    Dependencia que provee una sesion de base de datos.

    Yields:
        Session: Sesion de SQLAlchemy

    Uso:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependencia que obtiene el usuario actual desde el token JWT.

    Args:
        credentials: Credenciales HTTP Bearer (token JWT)
        db: Sesion de base de datos

    Returns:
        User: Usuario autenticado

    Raises:
        HTTPException: Si el token es invalido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extraer token del header
        token = credentials.credentials

        # Decodificar token
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception

        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")

        if email is None or user_id is None:
            raise credentials_exception

        token_data = TokenData(email=email, user_id=user_id)

    except JWTError:
        raise credentials_exception

    # Buscar usuario en DB
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependencia que verifica que el usuario este activo.

    Args:
        current_user: Usuario actual (de get_current_user)

    Returns:
        User: Usuario activo

    Raises:
        HTTPException: Si el usuario esta inactivo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependencia que requiere que el usuario sea admin.

    Args:
        current_user: Usuario actual

    Returns:
        User: Usuario admin

    Raises:
        HTTPException: Si el usuario no es admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de administrador"
        )
    return current_user


async def require_super_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependencia que requiere que el usuario sea super admin.

    Args:
        current_user: Usuario actual

    Returns:
        User: Usuario super admin

    Raises:
        HTTPException: Si el usuario no es super admin
    """
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requiere permisos de super administrador"
        )
    return current_user


async def get_device_from_api_key(
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Dependencia para autenticar devices ESP32 mediante API Key.

    Args:
        x_api_key: API Key en el header X-API-Key
        db: Sesion de base de datos

    Returns:
        Device: Device autenticado

    Raises:
        HTTPException: Si la API Key es invalida
    """
    from app.models.device import Device
    from app.core.security import validate_device_api_key

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header requerido"
        )

    # Buscar device por API key
    # NOTA: Aqui deberiamos buscar en la DB si guardamos las API keys
    # Por ahora validamos contra el device_eui
    device = db.query(Device).filter(Device.device_eui == x_api_key.split("_")[0]).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key invalida"
        )

    # Validar API key (opcional: implementar validacion HMAC)
    # if not validate_device_api_key(x_api_key, device.device_eui):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="API Key invalida"
    #     )

    return device
