"""
Endpoints de Devices (GET, POST, PATCH, DELETE, schema).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, require_admin
from app.models.device import Device
from app.models.user import User
from app.schemas.device import Device as DeviceSchema, DeviceCreate, DeviceUpdate, DeviceSchema as DeviceSchemaResponse, DeviceVariableSchema


router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get("", response_model=List[DeviceSchema], summary="Listar devices")
def list_devices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todos los devices accesibles por el usuario.

    Args:
        skip: Numero de registros a saltar (paginacion)
        limit: Numero maximo de registros a retornar
        db: Sesion de base de datos
        current_user: Usuario autenticado

    Returns:
        List[DeviceSchema]: Lista de devices
    """
    query = db.query(Device)

    # Si no es super_admin, filtrar por locations permitidas
    if not current_user.is_super_admin and current_user.allowed_location_ids:
        # TODO: Implementar filtro por locations cuando tengamos relaciones cargadas
        pass

    devices = query.offset(skip).limit(limit).all()
    return devices


@router.get("/{device_id}", response_model=DeviceSchema, summary="Obtener device por ID")
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene un device por su ID.

    Args:
        device_id: ID del device
        db: Sesion de base de datos
        current_user: Usuario autenticado

    Returns:
        DeviceSchema: Device encontrado

    Raises:
        HTTPException 404: Si el device no existe
    """
    device = db.query(Device).filter(Device.id == device_id).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device con ID {device_id} no encontrado"
        )

    return device


@router.post("", response_model=DeviceSchema, status_code=status.HTTP_201_CREATED, summary="Crear device")
def create_device(
    device_data: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Crea un nuevo device (solo admins).

    Args:
        device_data: Datos del device a crear
        db: Sesion de base de datos
        current_user: Usuario admin

    Returns:
        DeviceSchema: Device creado

    Raises:
        HTTPException 400: Si el device_eui ya existe
    """
    # Verificar que el device_eui no exista
    existing_device = db.query(Device).filter(Device.device_eui == device_data.device_eui).first()
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device con EUI '{device_data.device_eui}' ya existe"
        )

    # Crear device
    device = Device(**device_data.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)

    return device


@router.patch("/{device_id}", response_model=DeviceSchema, summary="Actualizar device")
def update_device(
    device_id: int,
    device_data: DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Actualiza un device existente (solo admins).

    Args:
        device_id: ID del device a actualizar
        device_data: Datos a actualizar
        db: Sesion de base de datos
        current_user: Usuario admin

    Returns:
        DeviceSchema: Device actualizado

    Raises:
        HTTPException 404: Si el device no existe
    """
    device = db.query(Device).filter(Device.id == device_id).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device con ID {device_id} no encontrado"
        )

    # Actualizar campos
    update_data = device_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)

    db.commit()
    db.refresh(device)

    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar device")
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Elimina un device (solo admins).

    Args:
        device_id: ID del device a eliminar
        db: Sesion de base de datos
        current_user: Usuario admin

    Raises:
        HTTPException 404: Si el device no existe
    """
    device = db.query(Device).filter(Device.id == device_id).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device con ID {device_id} no encontrado"
        )

    db.delete(device)
    db.commit()

    return None


@router.get("/{device_id}/schema", response_model=DeviceSchemaResponse, summary="Obtener schema del device")
def get_device_schema(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene el schema de variables que el device envia.

    Este endpoint permite al frontend auto-generar graficos sin conocer
    de antemano que variables envia cada device.

    NOTA: En esta implementacion inicial, retorna un schema hardcodeado.
    En produccion, deberia auto-descubrir el schema del ultimo reading.

    Args:
        device_id: ID del device
        db: Sesion de base de datos
        current_user: Usuario autenticado

    Returns:
        DeviceSchemaResponse: Schema de variables

    Raises:
        HTTPException 404: Si el device no existe
    """
    device = db.query(Device).filter(Device.id == device_id).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device con ID {device_id} no encontrado"
        )

    # TODO: Auto-descubrir schema del ultimo reading
    # Por ahora retornamos un schema de ejemplo
    schema = DeviceSchemaResponse(
        device_id=device.id,
        variables=[
            DeviceVariableSchema(
                key="temp_c",
                label="Temperatura",
                unit="°C",
                type="float",
                color="#ff6b6b"
            ),
            DeviceVariableSchema(
                key="humidity_pct",
                label="Humedad Relativa",
                unit="%",
                type="float",
                color="#4ecdc4"
            ),
            DeviceVariableSchema(
                key="battery_mv",
                label="Bateria",
                unit="mV",
                type="int",
                color="#95e1d3"
            ),
        ]
    )

    return schema
