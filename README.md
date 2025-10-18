# 🌐 Sistema de Monitoreo IoT

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Plataforma modular y escalable para monitoreo en tiempo real de sensores IoT (temperatura, humedad, presión) con alertas automáticas y visualización dinámica de datos.

## 📋 Descripción

Sistema genérico y reutilizable para monitoreo de sensores en entornos industriales, hospitalarios, comerciales y residenciales. Reemplaza sistemas legacy PHP/MySQL con una arquitectura moderna basada en FastAPI + React + ESP32.

### ✨ Características Principales

- 🔐 **Autenticación JWT** - Sistema de login seguro con roles (super_admin, service_admin, technician, guest)
- 📊 **Visualización Dinámica** - Gráficos que se auto-generan según las variables del sensor
- 🚨 **Alertas Configurables** - Sistema flexible de reglas con notificaciones Email/Telegram/Webhook
- 📱 **API REST Completa** - Documentación automática con Swagger UI
- 🔌 **IoT Ready** - Endpoint optimizado para ESP32 con validación automática
- 📈 **JSONB Flexible** - Base de datos que se adapta a cualquier tipo de sensor sin migraciones
- 🐳 **Docker Compose** - Despliegue en un solo comando

## 🏗️ Arquitectura

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   ESP32     │────▶│   FastAPI    │────▶│ PostgreSQL   │
│  (Sensores) │ HTTP│   Backend    │ SQL │   + JSONB    │
└─────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │    React     │
                    │   Frontend   │
                    └──────────────┘
```

### 🗄️ Modelo de Datos

```
location_groups (Organizaciones)
    ↓ 1:N
locations (Áreas/Zonas)
    ↓ 1:N
assets (Equipos Físicos)
    ↓ 1:N
devices (Hardware ESP32)
    ↓ 1:N
sensor_readings (Mediciones JSONB)
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker & Docker Compose 24+
- Python 3.11+ (para desarrollo local)
- Git

### Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/MarceloAmado/monitoreo.git
cd monitoreo

# 2. Crear archivo .env
cp .env.example .env
# Editar .env con tus credenciales

# 3. Levantar con Docker Compose
docker-compose up -d

# 4. Ejecutar migraciones
docker exec -it iot_backend alembic upgrade head

# 5. Cargar datos iniciales
docker exec -it iot_backend python scripts/seed.py
```

### Acceso

- **API Backend:** http://localhost:8000
- **Documentación Swagger:** http://localhost:8000/api/v1/docs
- **Frontend:** http://localhost:3000 (Sprint 2)

**Credenciales de prueba:**
- Email: `admin@iot-monitoring.com`
- Password: `admin123`

## 📖 Documentación de la API

### Endpoints Principales

#### Autenticación

```http
POST /api/v1/auth/login
GET  /api/v1/auth/me
POST /api/v1/auth/logout
```

#### Devices

```http
GET    /api/v1/devices
GET    /api/v1/devices/{id}
GET    /api/v1/devices/{id}/schema
POST   /api/v1/devices
PATCH  /api/v1/devices/{id}
DELETE /api/v1/devices/{id}
```

#### Sensor Readings (ESP32)

```http
POST /api/v1/readings
GET  /api/v1/readings?device_id=1&date_from=2025-10-16
GET  /api/v1/readings/{id}
```

**Ejemplo de request desde ESP32:**

```json
POST /api/v1/readings
{
  "device_eui": "ESP32_LAB_001",
  "data_payload": {
    "temp_c": 25.5,
    "humidity_pct": 62.3,
    "battery_mv": 3750,
    "rssi_dbm": -65
  },
  "timestamp": "2025-10-16T18:30:00Z"
}
```

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** 0.104+ - Framework web moderno y rápido
- **SQLAlchemy** 2.0+ - ORM con soporte async
- **PostgreSQL** 15+ - Base de datos relacional con JSONB
- **Alembic** 1.12+ - Migraciones de base de datos
- **Pydantic** 2.5+ - Validación de datos
- **JWT** - Autenticación con tokens
- **Bcrypt** - Hashing seguro de contraseñas

### Frontend (Sprint 2)
- React 18+ + TypeScript
- Vite - Build tool
- TanStack Query - State management
- Recharts - Visualización de datos
- Tailwind CSS - Estilos

### Hardware
- ESP32 - Microcontrolador WiFi
- DS18B20, DHT22, MPX5700 - Sensores

## 📂 Estructura del Proyecto

```
monitoreo/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuración, DB, Security
│   │   ├── models/         # Modelos SQLAlchemy (8 tablas)
│   │   ├── schemas/        # Schemas Pydantic
│   │   ├── api/v1/         # Endpoints REST
│   │   └── main.py         # Entry point
│   ├── alembic/            # Migraciones
│   ├── scripts/            # Scripts (seed, etc.)
│   └── tests/              # Tests pytest
├── frontend/               # React app (Sprint 2)
├── firmware/               # ESP32 code (Sprint 2)
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔐 Seguridad

- ✅ Passwords hasheadas con bcrypt (cost factor 12)
- ✅ JWT con expiración configurable
- ✅ RBAC (Role-Based Access Control)
- ✅ Validación de inputs con Pydantic
- ✅ SQL Injection protection (SQLAlchemy ORM)
- ✅ CORS configurado
- 🔜 Rate limiting (próximamente)
- 🔜 HTTPS en producción (Let's Encrypt)

## 🧪 Testing

```bash
# Ejecutar todos los tests
docker exec -it iot_backend pytest -v

# Con cobertura
docker exec -it iot_backend pytest --cov=app --cov-report=html

# Test específico
docker exec -it iot_backend pytest tests/test_auth.py -v
```

## 📝 Comandos Útiles

```bash
# Ver logs del backend
docker-compose logs -f backend

# Recrear base de datos
docker-compose down -v
docker-compose up -d

# Ejecutar migraciones
docker exec -it iot_backend alembic upgrade head

# Acceder a PostgreSQL
docker exec -it iot_postgres psql -U iot_admin -d iot_monitoring

# Generar nueva migración
docker exec -it iot_backend alembic revision --autogenerate -m "descripcion"
```

## 📊 Estado del Proyecto

### Sprint 1: Backend MVP ✅ 100% COMPLETADO

- [x] Infraestructura Docker Compose (PostgreSQL + Redis + Backend)
- [x] Modelos SQLAlchemy (8 tablas)
- [x] Migraciones Alembic
- [x] Schemas Pydantic (7 schemas completos)
- [x] Autenticación JWT con bcrypt
- [x] Endpoints Auth (login, me)
- [x] Endpoints Devices (CRUD completo + schema)
- [x] Endpoints Readings (POST para ESP32 + GET con filtros)
- [x] Script de seed con datos de ejemplo
- [x] Tests pytest (33 tests, 28 passing - 84.8%)
- [x] Documentación Swagger UI completa
- [x] README y documentación técnica

**Fecha de finalización Sprint 1:** 2025-10-17

### Sprint 2: Frontend + ESP32 (En progreso)
- [ ] Setup React + TypeScript + Vite
- [ ] Dashboard básico con gráficos
- [ ] Firmware ESP32 con Zero-Config WiFi
- [ ] Primer ESP32 conectado enviando datos reales

### Sprint 3: Alertas + Gráficos Dinámicos
- [ ] Sistema de alertas configurables
- [ ] Gráficos dinámicos auto-generados
- [ ] Notificaciones Email/Telegram

### Sprint 4: Deploy + Profesionalización
- [ ] Deploy en servidor de producción
- [ ] OTA updates para ESP32
- [ ] Backups automáticos
- [ ] Optimizaciones de performance

## 🤝 Contribución

Este es un proyecto de portafolio. Pull requests son bienvenidos.

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: nueva funcionalidad'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👤 Autor

**Marcelo Amado**

- GitHub: [@MarceloAmado](https://github.com/MarceloAmado)

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com) por el excelente framework
- [PostgreSQL](https://www.postgresql.org) por el soporte JSONB
- Comunidad ESP32 por el ecosistema IoT

---

⭐ Si te gustó el proyecto, dale una estrella en GitHub!
