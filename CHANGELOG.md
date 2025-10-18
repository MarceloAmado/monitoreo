# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Por agregar
- Frontend React + TypeScript + Vite
- Gráficos dinámicos con Recharts
- Sistema de alertas configurables
- Firmware ESP32 con Zero-Config WiFi
- Notificaciones Email/Telegram

## [0.1.0] - 2025-10-17

### ✅ Sprint 1: Backend MVP - COMPLETADO

#### Agregado
- **Infraestructura Docker Compose**
  - PostgreSQL 15 con healthcheck
  - Redis 7 para cache y sesiones
  - Backend FastAPI con hot reload
  - Red interna Docker configurada

- **Base de Datos**
  - 8 tablas relacionales creadas con Alembic
  - Migraciones versionadas
  - Índices optimizados para queries frecuentes
  - Soporte JSONB para datos flexibles de sensores

- **Modelos de Datos (SQLAlchemy 2.0)**
  - `LocationGroup` - Organizaciones/Clientes
  - `Location` - Áreas/Zonas
  - `Asset` - Equipos físicos monitoreados
  - `Device` - Hardware ESP32
  - `SensorReading` - Mediciones con JSONB
  - `User` - Autenticación RBAC
  - `AlertRule` - Configuración de alertas
  - `AlertHistory` - Log de alertas

- **Schemas Pydantic (7 schemas completos)**
  - Validación automática de datos
  - Documentación OpenAPI generada
  - Type safety end-to-end

- **Autenticación y Seguridad**
  - JWT con expiración configurable (60min)
  - Bcrypt para hashing de contraseñas (cost factor 12)
  - RBAC con 4 roles: super_admin, service_admin, technician, guest
  - API keys para devices ESP32
  - CORS configurado
  - Validación de contraseñas fuertes

- **API REST (15+ endpoints)**
  - **Auth:**
    - `POST /api/v1/auth/login` - Login con JWT
    - `GET /api/v1/auth/me` - Usuario actual
  - **Devices:**
    - `GET /api/v1/devices` - Listar devices
    - `GET /api/v1/devices/{id}` - Detalle de device
    - `GET /api/v1/devices/{id}/schema` - Schema de variables
    - `POST /api/v1/devices` - Crear device
    - `PATCH /api/v1/devices/{id}` - Actualizar device
    - `DELETE /api/v1/devices/{id}` - Eliminar device
  - **Readings (crítico para ESP32):**
    - `POST /api/v1/readings` - Enviar lectura desde ESP32
    - `GET /api/v1/readings` - Listar con filtros
    - `GET /api/v1/readings/{id}` - Detalle de lectura
  - **Health:**
    - `GET /` - Info de la API
    - `GET /api/v1/health` - Estado del sistema (DB + Redis)

- **Scripts y Utilidades**
  - Script de seed con datos de ejemplo
  - Healthchecks para PostgreSQL y Redis
  - Logging estructurado con tiempos de respuesta
  - Exception handlers personalizados

- **Tests Automatizados**
  - 33 tests pytest implementados
  - 28 tests passing (84.8% success rate)
  - Tests de autenticación (14 tests)
  - Tests de readings (19 tests)
  - Cobertura de casos edge

- **Documentación**
  - Swagger UI en `/api/v1/docs`
  - ReDoc en `/api/v1/redoc`
  - README.md completo con instrucciones
  - CLAUDE.md con arquitectura detallada
  - Documentación inline en español

#### Características Técnicas
- FastAPI 0.104+ con async support
- SQLAlchemy 2.0 ORM
- PostgreSQL 15 con JSONB
- Redis 7 para cache
- Alembic para migraciones
- Pydantic 2.5+ para validación
- Docker Compose para desarrollo

#### Datos de Ejemplo Incluidos
- 1 Super Admin (email: admin@iot-monitoring.com)
- 1 Location Group: "Hospital de Prueba"
- 1 Location: "Laboratorio - Química"
- 1 Asset: "Heladera_Quimica_001"
- 1 Device: "ESP32_LAB_001"

#### Mejoras de Performance
- Connection pooling en PostgreSQL (10 conexiones + 20 overflow)
- Pool pre-ping para verificar conexiones
- Índices en columnas frecuentemente consultadas
- JSONB GIN index para búsquedas rápidas en payloads

#### Seguridad
- Passwords nunca en plaintext
- JWT firmado con HS256
- Protección contra SQL injection (ORM)
- Validación de inputs con Pydantic
- Protección contra timing attacks en comparación de API keys

### Probado
- ✅ Login y autenticación JWT
- ✅ CRUD de devices
- ✅ Envío y consulta de readings
- ✅ Health checks de DB y Redis
- ✅ Migraciones de base de datos
- ✅ Script de seed
- ✅ Documentación Swagger UI

### Notas Técnicas
- Sistema diseñado para ser genérico y reutilizable
- JSONB permite agregar nuevos sensores sin migraciones
- Arquitectura preparada para escalabilidad horizontal
- Hot reload en desarrollo para mayor productividad

---

## Formato del Changelog

### Tipos de cambios
- `Agregado` para funcionalidades nuevas
- `Cambiado` para cambios en funcionalidades existentes
- `Deprecado` para funcionalidades que serán removidas
- `Removido` para funcionalidades removidas
- `Corregido` para corrección de bugs
- `Seguridad` para vulnerabilidades corregidas

---

**Leyenda de Versiones:**
- **Major.Minor.Patch** (Semantic Versioning)
- Major: Cambios incompatibles en la API
- Minor: Nuevas funcionalidades compatibles
- Patch: Corrección de bugs compatible
