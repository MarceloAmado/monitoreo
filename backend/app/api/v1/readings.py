"""
Endpoints de SensorReadings (POST desde ESP32, GET con filtros).
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.device import Device
from app.models.sensor_reading import SensorReading
from app.models.user import User
from app.schemas.sensor_reading import SensorReadingCreate, SensorReading as SensorReadingSchema


router = APIRouter(prefix="/readings", tags=["Sensor Readings"])


@router.post("", response_model=SensorReadingSchema, status_code=status.HTTP_201_CREATED, summary="Crear reading (ESP32)")
def create_reading(
    reading_data: SensorReadingCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo sensor reading (usado por ESP32).

    Este es el endpoint CRITICO que los devices ESP32 llaman cada vez
    que toman una medicion. Debe ser rapido y eficiente.

    NOTA: En esta version inicial no requiere autenticacion para simplificar.
    En produccion deberia validar X-API-Key header.

    Args:
        reading_data: Datos de la medicion (device_eui, data_payload, timestamp)
        db: Sesion de base de datos

    Returns:
        SensorReadingSchema: Reading creado

    Raises:
        HTTPException 404: Si el device no existe
    """
    # Buscar device por EUI
    device = db.query(Device).filter(Device.device_eui == reading_data.device_eui).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device con EUI '{reading_data.device_eui}' no encontrado"
        )

    # Calcular quality_score basico (en produccion seria mas sofisticado)
    quality_score = calculate_quality_score(reading_data.data_payload)

    # Crear reading
    reading = SensorReading(
        device_id=device.id,
        data_payload=reading_data.data_payload,
        quality_score=quality_score,
        timestamp=reading_data.timestamp or datetime.utcnow(),
        processed=False
    )

    db.add(reading)

    # Actualizar last_seen_at del device
    device.last_seen_at = datetime.utcnow()

    db.commit()
    db.refresh(reading)

    return reading


@router.get("", response_model=List[SensorReadingSchema], summary="Listar readings")
def list_readings(
    device_id: Optional[int] = Query(None, description="Filtrar por device ID"),
    date_from: Optional[datetime] = Query(None, description="Fecha desde (UTC)"),
    date_to: Optional[datetime] = Query(None, description="Fecha hasta (UTC)"),
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Registros a retornar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista sensor readings con filtros opcionales.

    Args:
        device_id: Filtrar por device ID
        date_from: Fecha desde (UTC)
        date_to: Fecha hasta (UTC)
        skip: Registros a saltar (paginacion)
        limit: Registros a retornar (max 1000)
        db: Sesion de base de datos
        current_user: Usuario autenticado

    Returns:
        List[SensorReadingSchema]: Lista de readings
    """
    query = db.query(SensorReading)

    # Aplicar filtros
    if device_id:
        query = query.filter(SensorReading.device_id == device_id)

    if date_from:
        query = query.filter(SensorReading.timestamp >= date_from)

    if date_to:
        query = query.filter(SensorReading.timestamp <= date_to)
    else:
        # Por defecto, solo ultimas 24 horas si no se especifica date_to
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=1)
            query = query.filter(SensorReading.timestamp >= date_from)

    # Ordenar por timestamp descendente (mas recientes primero)
    query = query.order_by(SensorReading.timestamp.desc())

    # Aplicar paginacion
    readings = query.offset(skip).limit(limit).all()

    return readings


@router.get("/{reading_id}", response_model=SensorReadingSchema, summary="Obtener reading por ID")
def get_reading(
    reading_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene un reading por su ID.

    Args:
        reading_id: ID del reading
        db: Sesion de base de datos
        current_user: Usuario autenticado

    Returns:
        SensorReadingSchema: Reading encontrado

    Raises:
        HTTPException 404: Si el reading no existe
    """
    reading = db.query(SensorReading).filter(SensorReading.id == reading_id).first()

    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reading con ID {reading_id} no encontrado"
        )

    return reading


def calculate_quality_score(data_payload: dict) -> float:
    """
    Calcula un score de calidad basico para el reading.

    En produccion, esto seria mas sofisticado:
    - Detectar valores fuera de rango fisico
    - Detectar cambios bruscos sospechosos
    - Verificar timestamp valido
    - etc.

    Args:
        data_payload: Datos del sensor

    Returns:
        float: Score entre 0.0 y 1.0
    """
    score = 1.0

    # Verificar que haya al menos una variable
    if not data_payload or len(data_payload) == 0:
        return 0.0

    # Detectar valores de error (-999)
    for key, value in data_payload.items():
        if isinstance(value, (int, float)):
            if value == -999 or value == -999.0:
                score -= 0.3

    # Asegurar que el score este entre 0 y 1
    return max(0.0, min(1.0, score))
