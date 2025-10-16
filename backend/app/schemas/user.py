"""
Schemas Pydantic para User.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserBase(BaseModel):
    """Schema base para User (campos comunes)."""
    email: EmailStr = Field(..., description="Email unico del usuario")
    role: str = Field(..., max_length=32, description="Rol: super_admin, service_admin, technician, guest")
    allowed_location_ids: Optional[List[int]] = Field(None, description="IDs de locations permitidas")
    first_name: str = Field(..., max_length=64, description="Nombre")
    last_name: str = Field(..., max_length=64, description="Apellido")
    is_active: bool = Field(default=True, description="Usuario activo")


class UserCreate(UserBase):
    """
    Schema para crear un User.

    Incluye el campo password en plaintext (se hasheara en el backend).
    """
    password: str = Field(..., min_length=8, description="Contrasena en plaintext (min 8 caracteres)")


class UserUpdate(BaseModel):
    """Schema para actualizar un User (todos los campos opcionales)."""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, description="Nueva contrasena (opcional)")
    role: Optional[str] = Field(None, max_length=32)
    allowed_location_ids: Optional[List[int]] = None
    first_name: Optional[str] = Field(None, max_length=64)
    last_name: Optional[str] = Field(None, max_length=64)
    is_active: Optional[bool] = None


class User(UserBase):
    """
    Schema para respuesta de User (incluye campos de DB).

    NOTA: NO incluye password_hash por seguridad.
    """
    id: int
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
