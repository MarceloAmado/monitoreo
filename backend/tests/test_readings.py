"""
Tests para endpoints de sensor readings (POST /readings, GET /readings).

Este es un endpoint CRITICO ya que los ESP32 envian datos aqui.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.sensor_reading import SensorReading


class TestCreateReading:
    """Tests para POST /api/v1/readings (endpoint CRITICO para ESP32)"""

    def test_create_reading_success(
        self,
        client: TestClient,
        device: Device
    ):
        """Test de creacion exitosa de un reading desde ESP32."""
        reading_data = {
            "device_eui": "ESP32_TEST_001",
            "data_payload": {
                "temp_c": 25.5,
                "humidity_pct": 62.3,
                "battery_mv": 3750,
                "rssi_dbm": -65
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        response = client.post("/api/v1/readings", json=reading_data)

        assert response.status_code == 201
        data = response.json()
        assert data["device_id"] == device.id
        assert data["data_payload"] == reading_data["data_payload"]
        assert "quality_score" in data
        assert data["processed"] is False
        assert "id" in data

    def test_create_reading_auto_timestamp(
        self,
        client: TestClient,
        device: Device
    ):
        """Test de que si no se envia timestamp, se asigna automaticamente."""
        reading_data = {
            "device_eui": "ESP32_TEST_001",
            "data_payload": {
                "temp_c": 24.0
            }
            # Sin timestamp
        }

        response = client.post("/api/v1/readings", json=reading_data)

        assert response.status_code == 201
        data = response.json()
        assert "timestamp" in data
        # Verificar que el timestamp es reciente (ultimos 10 segundos)
        timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        now = datetime.utcnow()
        assert (now - timestamp).total_seconds() < 10

    def test_create_reading_updates_device_last_seen(
        self,
        client: TestClient,
        device: Device,
        db_session: Session
    ):
        """Test de que crear un reading actualiza device.last_seen_at."""
        # Guardar last_seen_at inicial
        initial_last_seen = device.last_seen_at

        reading_data = {
            "device_eui": "ESP32_TEST_001",
            "data_payload": {"temp_c": 26.0}
        }

        response = client.post("/api/v1/readings", json=reading_data)
        assert response.status_code == 201

        # Refrescar device desde DB
        db_session.refresh(device)

        # Verificar que last_seen_at se actualizo
        assert device.last_seen_at != initial_last_seen
        assert device.last_seen_at is not None

    def test_create_reading_device_not_found(self, client: TestClient):
        """Test de crear reading con device_eui inexistente."""
        reading_data = {
            "device_eui": "ESP32_NONEXISTENT",
            "data_payload": {"temp_c": 25.0}
        }

        response = client.post("/api/v1/readings", json=reading_data)

        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"].lower()

    def test_create_reading_empty_payload(
        self,
        client: TestClient,
        device: Device
    ):
        """Test de crear reading con payload vacio (deberia fallar validacion)."""
        reading_data = {
            "device_eui": "ESP32_TEST_001",
            "data_payload": {}
        }

        response = client.post("/api/v1/readings", json=reading_data)

        # Puede ser 400 o 422 dependiendo de validacion
        assert response.status_code in [400, 422]

    def test_create_reading_quality_score_calculation(
        self,
        client: TestClient,
        device: Device
    ):
        """Test de que quality_score se calcula correctamente."""
        # Payload con valores normales (deberia tener quality_score alto)
        reading_data = {
            "device_eui": "ESP32_TEST_001",
            "data_payload": {
                "temp_c": 25.0,
                "humidity_pct": 60.0
            }
        }

        response = client.post("/api/v1/readings", json=reading_data)
        assert response.status_code == 201
        data = response.json()
        assert data["quality_score"] > 0.5  # Deberia ser bueno

    def test_create_reading_low_quality_score(
        self,
        client: TestClient,
        device: Device
    ):
        """Test de que valores sospechosos generan quality_score bajo."""
        # Payload con valor de error (-999)
        reading_data = {
            "device_eui": "ESP32_TEST_001",
            "data_payload": {
                "temp_c": -999.0,  # Valor de error
                "humidity_pct": 60.0
            }
        }

        response = client.post("/api/v1/readings", json=reading_data)
        assert response.status_code == 201
        data = response.json()
        # Quality score deberia ser bajo por el valor de error
        assert data["quality_score"] < 0.5

    def test_create_reading_multiple_sensors(
        self,
        client: TestClient,
        device: Device
    ):
        """Test de crear reading con multiples sensores en el payload."""
        reading_data = {
            "device_eui": "ESP32_TEST_001",
            "data_payload": {
                "temp_c": 25.5,
                "humidity_pct": 62.3,
                "pressure_bar": 1.013,
                "battery_mv": 3750,
                "rssi_dbm": -65,
                "custom_sensor": 123.45
            }
        }

        response = client.post("/api/v1/readings", json=reading_data)

        assert response.status_code == 201
        data = response.json()
        # Verificar que todos los campos se guardaron
        assert data["data_payload"]["temp_c"] == 25.5
        assert data["data_payload"]["humidity_pct"] == 62.3
        assert data["data_payload"]["pressure_bar"] == 1.013
        assert data["data_payload"]["custom_sensor"] == 123.45


class TestGetReadings:
    """Tests para GET /api/v1/readings"""

    def test_get_readings_list(
        self,
        client: TestClient,
        auth_headers_admin: dict,
        device: Device,
        db_session: Session
    ):
        """Test de obtener lista de readings."""
        # Crear algunos readings de prueba
        for i in range(5):
            reading = SensorReading(
                device_id=device.id,
                data_payload={"temp_c": 20.0 + i},
                quality_score=0.95,
                processed=False,
                timestamp=datetime.utcnow()
            )
            db_session.add(reading)
        db_session.commit()

        response = client.get("/api/v1/readings", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5

    def test_get_readings_filter_by_device(
        self,
        client: TestClient,
        auth_headers_admin: dict,
        device: Device,
        db_session: Session
    ):
        """Test de filtrar readings por device_id."""
        # Crear readings para el device de prueba
        for i in range(3):
            reading = SensorReading(
                device_id=device.id,
                data_payload={"temp_c": 20.0 + i},
                quality_score=0.95,
                timestamp=datetime.utcnow()
            )
            db_session.add(reading)
        db_session.commit()

        response = client.get(
            f"/api/v1/readings?device_id={device.id}",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Verificar que todos son del device correcto
        for reading in data:
            assert reading["device_id"] == device.id

    def test_get_readings_filter_by_date_range(
        self,
        client: TestClient,
        auth_headers_admin: dict,
        device: Device,
        db_session: Session
    ):
        """Test de filtrar readings por rango de fechas."""
        now = datetime.utcnow()

        # Crear readings en diferentes fechas
        old_reading = SensorReading(
            device_id=device.id,
            data_payload={"temp_c": 20.0},
            quality_score=0.95,
            timestamp=now - timedelta(days=10)
        )
        recent_reading = SensorReading(
            device_id=device.id,
            data_payload={"temp_c": 25.0},
            quality_score=0.95,
            timestamp=now
        )
        db_session.add_all([old_reading, recent_reading])
        db_session.commit()

        # Filtrar solo readings de ultimas 24 horas
        date_from = (now - timedelta(days=1)).isoformat()
        response = client.get(
            f"/api/v1/readings?date_from={date_from}",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["data_payload"]["temp_c"] == 25.0

    def test_get_readings_unauthorized(self, client: TestClient):
        """Test de que GET /readings requiere autenticacion."""
        response = client.get("/api/v1/readings")

        assert response.status_code == 403  # Forbidden

    def test_get_readings_empty_list(
        self,
        client: TestClient,
        auth_headers_admin: dict
    ):
        """Test de obtener lista vacia cuando no hay readings."""
        response = client.get("/api/v1/readings", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_readings_pagination(
        self,
        client: TestClient,
        auth_headers_admin: dict,
        device: Device,
        db_session: Session
    ):
        """Test de paginacion de readings."""
        # Crear 25 readings
        for i in range(25):
            reading = SensorReading(
                device_id=device.id,
                data_payload={"temp_c": 20.0 + i},
                quality_score=0.95,
                timestamp=datetime.utcnow()
            )
            db_session.add(reading)
        db_session.commit()

        # Obtener primera pagina (skip=0, limit=10)
        response = client.get(
            "/api/v1/readings?skip=0&limit=10",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10

        # Obtener segunda pagina (skip=10, limit=10)
        response = client.get(
            "/api/v1/readings?skip=10&limit=10",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10


class TestGetReadingById:
    """Tests para GET /api/v1/readings/{id}"""

    def test_get_reading_by_id_success(
        self,
        client: TestClient,
        auth_headers_admin: dict,
        device: Device,
        db_session: Session
    ):
        """Test de obtener un reading por ID."""
        reading = SensorReading(
            device_id=device.id,
            data_payload={"temp_c": 25.5, "humidity_pct": 60.0},
            quality_score=0.95,
            timestamp=datetime.utcnow()
        )
        db_session.add(reading)
        db_session.commit()
        db_session.refresh(reading)

        response = client.get(
            f"/api/v1/readings/{reading.id}",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == reading.id
        assert data["device_id"] == device.id
        assert data["data_payload"]["temp_c"] == 25.5

    def test_get_reading_by_id_not_found(
        self,
        client: TestClient,
        auth_headers_admin: dict
    ):
        """Test de obtener reading con ID inexistente."""
        response = client.get(
            "/api/v1/readings/999999",
            headers=auth_headers_admin
        )

        assert response.status_code == 404

    def test_get_reading_by_id_unauthorized(
        self,
        client: TestClient,
        device: Device,
        db_session: Session
    ):
        """Test de que GET /readings/{id} requiere autenticacion."""
        reading = SensorReading(
            device_id=device.id,
            data_payload={"temp_c": 25.5},
            quality_score=0.95,
            timestamp=datetime.utcnow()
        )
        db_session.add(reading)
        db_session.commit()
        db_session.refresh(reading)

        response = client.get(f"/api/v1/readings/{reading.id}")

        assert response.status_code == 403  # Forbidden


class TestReadingsIntegration:
    """Tests de integracion end-to-end para el flujo completo."""

    def test_full_esp32_workflow(
        self,
        client: TestClient,
        auth_headers_admin: dict,
        device: Device,
        db_session: Session
    ):
        """
        Test de flujo completo de ESP32:
        1. ESP32 envia reading
        2. Backend almacena y actualiza last_seen
        3. Frontend obtiene readings
        """
        # 1. ESP32 envia datos
        esp32_payload = {
            "device_eui": "ESP32_TEST_001",
            "data_payload": {
                "temp_c": 25.5,
                "humidity_pct": 62.3,
                "battery_mv": 3750,
                "rssi_dbm": -65
            }
        }

        create_response = client.post("/api/v1/readings", json=esp32_payload)
        assert create_response.status_code == 201
        reading_id = create_response.json()["id"]

        # 2. Verificar que se guardo correctamente
        db_session.refresh(device)
        assert device.last_seen_at is not None
        assert device.is_online is True

        # 3. Frontend obtiene el reading
        get_response = client.get(
            f"/api/v1/readings/{reading_id}",
            headers=auth_headers_admin
        )
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["data_payload"]["temp_c"] == 25.5
        assert data["data_payload"]["humidity_pct"] == 62.3

    def test_multiple_devices_readings(
        self,
        client: TestClient,
        auth_headers_admin: dict,
        device: Device,
        asset,
        db_session: Session
    ):
        """Test de que multiples devices pueden enviar readings simultaneamente."""
        # Crear segundo device
        device2 = Device(
            asset_id=asset.id,
            device_eui="ESP32_TEST_002",
            name="ESP32 Test 002",
            status="active"
        )
        db_session.add(device2)
        db_session.commit()

        # Ambos devices envian readings
        payload1 = {
            "device_eui": "ESP32_TEST_001",
            "data_payload": {"temp_c": 25.0}
        }
        payload2 = {
            "device_eui": "ESP32_TEST_002",
            "data_payload": {"temp_c": 30.0}
        }

        response1 = client.post("/api/v1/readings", json=payload1)
        response2 = client.post("/api/v1/readings", json=payload2)

        assert response1.status_code == 201
        assert response2.status_code == 201

        # Verificar que se pueden filtrar por device
        response = client.get(
            f"/api/v1/readings?device_id={device.id}",
            headers=auth_headers_admin
        )
        data = response.json()
        assert len(data) == 1
        assert data[0]["data_payload"]["temp_c"] == 25.0
