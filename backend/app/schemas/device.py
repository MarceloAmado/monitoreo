"""
Schemas Pydantic para Device.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class DeviceBase(BaseModel):
    """Schema base para Device (campos comunes)."""
    asset_id: Optional[int] = Field(None, description="ID del asset al que esta asignado")
    device_eui: str = Field(..., max_length=64, description="ID unico del device")
    name: str = Field(..., max_length=128, description="Nombre amigable del device")
    status: str = Field(default="active", max_length=32, description="Estado: active, inactive, maintenance, error")
    firmware_version: Optional[str] = Field(None, max_length=20, description="Version del firmware")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuracion del device")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Metadata adicional")


class DeviceCreate(DeviceBase):
    """Schema para crear un Device."""
    pass


class DeviceUpdate(BaseModel):
    """Schema para actualizar un Device (todos los campos opcionales)."""
    asset_id: Optional[int] = None
    device_eui: Optional[str] = Field(None, max_length=64)
    name: Optional[str] = Field(None, max_length=128)
    status: Optional[str] = Field(None, max_length=32)
    firmware_version: Optional[str] = Field(None, max_length=20)
    config: Optional[Dict[str, Any]] = None
    extra_data: Optional[Dict[str, Any]] = None


class Device(DeviceBase):
    """Schema para respuesta de Device (incluye campos de DB)."""
    id: int
    last_seen_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================
# Schema Discovery Schemas (para auto-generar graficos)
# ============================================

class DeviceVariableSchema(BaseModel):
    """
    Schema para una variable de sensor.

    Describe una variable individual que el device mide
    (temperatura, humedad, presion, etc.)
    """
    key: str = Field(..., description="Key en el JSONB: temp_c, humidity_pct, etc.")
    label: str = Field(..., description="Etiqueta amigable: Temperatura, Humedad, etc.")
    unit: str = Field(..., description="Unidad de medida: C, %, bar, etc.")
    type: str = Field(..., description="Tipo de dato: float, int, string")
    color: Optional[str] = Field(None, description="Color para graficos en hex: #ff6b6b")


class DeviceSchema(BaseModel):
    """
    Schema de variables que un device envia.

    Permite al frontend auto-generar graficos sin conocer
    de antemano que variables envia cada device.
    """
    device_id: int
    variables: List[DeviceVariableSchema]

    model_config = ConfigDict(from_attributes=True)
