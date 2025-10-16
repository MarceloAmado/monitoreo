# 🚀 Guía de Inicio Rápido - Sistema IoT Monitoring

## Requisitos Previos

### Software Necesario
- ✅ Docker Desktop (Windows/Mac) o Docker + Docker Compose (Linux)
- ✅ Node.js 18+ con npm
- ✅ Git (ya instalado)

### Verificar Instalaciones
```bash
# Verificar Docker
docker --version
docker compose version

# Verificar Node.js
node --version
npm --version
```

---

## 🐳 Paso 1: Levantar Backend con Docker Compose

### 1.1 Navegar al directorio del proyecto
```bash
cd "e:\Documentos\Marcelo\Trabajos Idea\Python\Idea_IoT"
```

### 1.2 Verificar que existe el archivo .env
```bash
ls -la | grep .env
```

Deberías ver `.env` en la lista. Si no existe, copia el ejemplo:
```bash
cp .env.example .env
```

### 1.3 Levantar PostgreSQL y Redis
```bash
docker compose up -d postgres redis
```

Esperar unos segundos hasta que los servicios estén saludables:
```bash
docker compose ps
```

Deberías ver:
```
NAME                  STATUS              PORTS
iot_postgres          Up (healthy)        0.0.0.0:5432->5432/tcp
iot_redis             Up                  0.0.0.0:6379->6379/tcp
```

### 1.4 Levantar el Backend FastAPI
```bash
docker compose up -d backend
```

### 1.5 Verificar logs del backend
```bash
docker compose logs -f backend
```

Deberías ver:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
✓ Database connection successful
```

Presiona `Ctrl+C` para salir de los logs.

---

## 🗄️ Paso 2: Ejecutar Migraciones y Seed

### 2.1 Ejecutar migraciones de Alembic
```bash
docker exec -it iot_backend alembic upgrade head
```

Salida esperada:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 5494f0ce411a, Initial migration create all tables
```

### 2.2 Ejecutar script de seed (datos iniciales)
```bash
docker exec -it iot_backend python scripts/seed.py
```

Salida esperada:
```
✓ Super Admin creado: admin@iot-monitoring.com
✓ LocationGroup creado: Hospital de Prueba
✓ Location creado: Laboratorio - Química
✓ Asset creado: Heladera_Química_001
✓ Device creado: ESP32_LAB_001
✓ Seed completado exitosamente!
```

### 2.3 Verificar que el backend responde
```bash
curl http://localhost:8000/api/v1/health
```

O abre en el navegador: http://localhost:8000/api/v1/docs

Deberías ver la documentación Swagger UI.

---

## ⚛️ Paso 3: Levantar Frontend React

### 3.1 Navegar al directorio del frontend
```bash
cd frontend
```

### 3.2 Instalar dependencias de Node.js
```bash
npm install
```

Esto tomará unos minutos la primera vez.

### 3.3 Verificar que existe .env en frontend
```bash
ls -la | grep .env
```

Debería existir `frontend/.env` con:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 3.4 Levantar el servidor de desarrollo
```bash
npm run dev
```

Salida esperada:
```
  VITE v5.0.8  ready in 1234 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## 🎉 Paso 4: Probar la Aplicación

### 4.1 Abrir el navegador
Abre tu navegador en: **http://localhost:3000**

Deberías ver la página de **Login**.

### 4.2 Iniciar sesión
Usa las credenciales del seed:
- **Email:** `admin@iot-monitoring.com`
- **Password:** `admin123`

### 4.3 Explorar el Dashboard
Después del login, deberías ver:
- ✅ Dashboard con 4 tarjetas de estadísticas
- ✅ Tabla con 1 device: "ESP32 Test 001"
- ✅ Estado: "Activo" pero "Fuera de línea" (porque no hay ESP32 real enviando datos)

### 4.4 Ver detalle del device
Haz clic en "Ver detalles →" del device ESP32_LAB_001.

Deberías ver:
- Información del device (Estado, Firmware, Última Actividad)
- Gráfico vacío (porque no hay lecturas aún)
- Mensaje: "No hay datos disponibles para las últimas 24 horas"

---

## 🧪 Paso 5: Simular Datos de un ESP32 (Opcional)

Para ver el gráfico funcionando, puedes simular datos de un ESP32 con curl:

### 5.1 Crear una lectura de prueba
```bash
curl -X POST http://localhost:8000/api/v1/readings \
  -H "Content-Type: application/json" \
  -d '{
    "device_eui": "ESP32_LAB_001",
    "data_payload": {
      "temp_c": 25.5,
      "humidity_pct": 62.3,
      "battery_mv": 3750,
      "rssi_dbm": -65
    }
  }'
```

### 5.2 Crear varias lecturas con diferentes temperaturas
```bash
# Temperatura 23°C
curl -X POST http://localhost:8000/api/v1/readings \
  -H "Content-Type: application/json" \
  -d '{"device_eui": "ESP32_LAB_001", "data_payload": {"temp_c": 23.0, "humidity_pct": 60.0}}'

# Temperatura 24°C
curl -X POST http://localhost:8000/api/v1/readings \
  -H "Content-Type: application/json" \
  -d '{"device_eui": "ESP32_LAB_001", "data_payload": {"temp_c": 24.0, "humidity_pct": 61.0}}'

# Temperatura 25°C
curl -X POST http://localhost:8000/api/v1/readings \
  -H "Content-Type: application/json" \
  -d '{"device_eui": "ESP32_LAB_001", "data_payload": {"temp_c": 25.0, "humidity_pct": 62.0}}'

# Temperatura 26°C
curl -X POST http://localhost:8000/api/v1/readings \
  -H "Content-Type: application/json" \
  -d '{"device_eui": "ESP32_LAB_001", "data_payload": {"temp_c": 26.0, "humidity_pct": 63.0}}'
```

### 5.3 Refrescar la página del frontend
Presiona `F5` en la página de Device Detail.

Ahora deberías ver:
- ✅ Gráfico con líneas de temperatura y humedad
- ✅ Tabla con las 4 lecturas recientes
- ✅ Device marcado como "En línea" (verde)

---

## 📊 Verificaciones Finales

### Backend (FastAPI)
- ✅ Swagger UI: http://localhost:8000/api/v1/docs
- ✅ Health check: http://localhost:8000/api/v1/health
- ✅ Login endpoint funcional
- ✅ Devices endpoint retorna 1 device
- ✅ Readings endpoint acepta datos

### Frontend (React)
- ✅ Login funcional con JWT
- ✅ Dashboard muestra estadísticas
- ✅ Tabla de devices renderiza correctamente
- ✅ Device Detail muestra gráficos
- ✅ Logout funciona (redirige a /login)

### Base de Datos
- ✅ PostgreSQL: 8 tablas creadas
- ✅ Seed data: 1 admin, 1 location_group, 1 location, 1 asset, 1 device

---

## 🛠️ Comandos Útiles

### Ver logs en tiempo real
```bash
# Logs del backend
docker compose logs -f backend

# Logs de PostgreSQL
docker compose logs -f postgres

# Logs de todos los servicios
docker compose logs -f
```

### Detener servicios
```bash
# Detener todos los servicios
docker compose down

# Detener y eliminar volúmenes (CUIDADO: borra la DB)
docker compose down -v
```

### Reiniciar servicios
```bash
# Reiniciar solo el backend
docker compose restart backend

# Reiniciar todos
docker compose restart
```

### Acceder a PostgreSQL
```bash
docker exec -it iot_postgres psql -U iot_admin -d iot_monitoring

# Dentro de psql:
\dt              # Listar tablas
SELECT * FROM users;
SELECT * FROM devices;
SELECT * FROM sensor_readings;
\q               # Salir
```

### Ejecutar tests del backend
```bash
docker exec -it iot_backend pytest -v
```

---

## 🐛 Troubleshooting

### Problema: "docker: command not found"
**Solución:** Instala Docker Desktop desde https://www.docker.com/products/docker-desktop

### Problema: "Port 8000 is already in use"
**Solución:**
```bash
# Ver qué está usando el puerto
netstat -ano | findstr :8000

# Detener Docker Compose
docker compose down

# Cambiar puerto en docker-compose.yml (8000 → 8001)
```

### Problema: "Backend no conecta a PostgreSQL"
**Solución:**
```bash
# Verificar que postgres esté healthy
docker compose ps

# Ver logs de postgres
docker compose logs postgres

# Reiniciar servicios
docker compose down && docker compose up -d
```

### Problema: "Frontend muestra error 401 Unauthorized"
**Solución:**
- Verificar que el backend esté corriendo: http://localhost:8000/api/v1/health
- Limpiar localStorage del navegador (F12 → Application → Local Storage → Clear All)
- Intentar login nuevamente

### Problema: "npm install falla"
**Solución:**
```bash
# Limpiar cache de npm
npm cache clean --force

# Eliminar node_modules y package-lock.json
rm -rf node_modules package-lock.json

# Reinstalar
npm install
```

### Problema: "No se ven datos en el gráfico"
**Solución:**
- Crear lecturas con curl (ver Paso 5)
- Verificar que el device_eui coincida: "ESP32_LAB_001"
- Refrescar la página (F5)

---

## 📝 Notas Importantes

### Datos de Prueba
- **Admin Email:** admin@iot-monitoring.com
- **Admin Password:** admin123
- **Device EUI:** ESP32_LAB_001

### Puertos Usados
- **Backend API:** 8000
- **Frontend React:** 3000
- **PostgreSQL:** 5432
- **Redis:** 6379

### Archivos de Configuración
- **Backend:** `.env` (raíz del proyecto)
- **Frontend:** `frontend/.env`
- **Docker:** `docker-compose.yml`

---

## 🎯 Próximos Pasos

1. ✅ Sistema funcionando localmente
2. ⏳ Implementar firmware ESP32 (Sprint 2 - Parte 2)
3. ⏳ Gráficos dinámicos con auto-discovery (Sprint 3)
4. ⏳ Sistema de alertas (Sprint 3)
5. ⏳ Deploy en producción (Sprint 4)

---

**¿Necesitas ayuda?**
- Revisa los logs: `docker compose logs -f`
- Verifica el Swagger UI: http://localhost:8000/api/v1/docs
- Consulta el README.md del backend o frontend

**¡Éxito con el proyecto! 🚀**
