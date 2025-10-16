"""
Script de Seed para Base de Datos.

Crea datos iniciales para desarrollo y testing:
- Super Admin user
- LocationGroup de ejemplo
- Location de ejemplo
- Asset de ejemplo
- Device de ejemplo
"""

import sys
import os

# Agregar el directorio raiz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, init_db
from app.core.security import hash_password
from app.models.user import User
from app.models.location import LocationGroup, Location
from app.models.asset import Asset
from app.models.device import Device


def seed_database():
    """
    Crea datos iniciales en la base de datos.
    """
    print("=" * 60)
    print("Iniciando seed de base de datos...")
    print("=" * 60)

    # Crear tablas si no existen
    print("\n1. Creando tablas...")
    init_db()
    print("   ✓ Tablas creadas")

    db = SessionLocal()

    try:
        # ===== 1. Crear Super Admin =====
        print("\n2. Creando Super Admin...")

        # Verificar si ya existe
        existing_admin = db.query(User).filter(User.email == "admin@iot-monitoring.com").first()

        if existing_admin:
            print("   ⚠ Super Admin ya existe, saltando...")
        else:
            admin = User(
                email="admin@iot-monitoring.com",
                password_hash=hash_password("admin123"),  # CAMBIAR EN PRODUCCION
                role="super_admin",
                first_name="Super",
                last_name="Admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("   ✓ Super Admin creado")
            print("     Email: admin@iot-monitoring.com")
            print("     Password: admin123")

        # ===== 2. Crear LocationGroup =====
        print("\n3. Creando LocationGroup de ejemplo...")

        existing_group = db.query(LocationGroup).filter(LocationGroup.name == "Hospital de Prueba").first()

        if existing_group:
            print("   ⚠ LocationGroup ya existe, saltando...")
            location_group = existing_group
        else:
            location_group = LocationGroup(
                name="Hospital de Prueba",
                description="Location group de ejemplo para desarrollo"
            )
            db.add(location_group)
            db.commit()
            db.refresh(location_group)
            print(f"   ✓ LocationGroup creado (ID: {location_group.id})")

        # ===== 3. Crear Location =====
        print("\n4. Creando Location de ejemplo...")

        existing_location = db.query(Location).filter(Location.code == "LAB-001").first()

        if existing_location:
            print("   ⚠ Location ya existe, saltando...")
            location = existing_location
        else:
            location = Location(
                location_group_id=location_group.id,
                name="Laboratorio - Quimica",
                code="LAB-001"
            )
            db.add(location)
            db.commit()
            db.refresh(location)
            print(f"   ✓ Location creado (ID: {location.id})")

        # ===== 4. Crear Asset =====
        print("\n5. Creando Asset de ejemplo...")

        existing_asset = db.query(Asset).filter(Asset.name == "Heladera_Quimica_001").first()

        if existing_asset:
            print("   ⚠ Asset ya existe, saltando...")
            asset = existing_asset
        else:
            asset = Asset(
                location_id=location.id,
                name="Heladera_Quimica_001",
                type="refrigerator",
                description="Heladera para almacenamiento de reactivos quimicos",
                extra_data={
                    "capacidad": "500L",
                    "marca": "Philco",
                    "modelo": "HPH-500",
                    "anio": 2023
                }
            )
            db.add(asset)
            db.commit()
            db.refresh(asset)
            print(f"   ✓ Asset creado (ID: {asset.id})")

        # ===== 5. Crear Device =====
        print("\n6. Creando Device de ejemplo...")

        existing_device = db.query(Device).filter(Device.device_eui == "ESP32_LAB_001").first()

        if existing_device:
            print("   ⚠ Device ya existe, saltando...")
        else:
            device = Device(
                asset_id=asset.id,
                device_eui="ESP32_LAB_001",
                name="ESP32 Laboratorio 001",
                status="active",
                firmware_version="v1.0.0",
                config={
                    "sampling_interval_sec": 300,
                    "wifi_ssid": "Hospital_IoT",
                    "sensors": ["DS18B20", "DHT22"]
                },
                extra_data={
                    "mac_address": "AA:BB:CC:DD:EE:01",
                    "hardware_version": "ESP32-WROOM-32"
                }
            )
            db.add(device)
            db.commit()
            db.refresh(device)
            print(f"   ✓ Device creado (ID: {device.id})")
            print(f"     EUI: {device.device_eui}")

        print("\n" + "=" * 60)
        print("✓ Seed completado exitosamente!")
        print("=" * 60)
        print("\n📌 Credenciales de acceso:")
        print("   Email: admin@iot-monitoring.com")
        print("   Password: admin123")
        print("\n📌 Device EUI para pruebas:")
        print("   ESP32_LAB_001")
        print("\n" + "=" * 60)

    except Exception as e:
        print(f"\n✗ Error durante el seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
