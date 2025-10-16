"""
Sistema de Monitoreo IoT
Entry Point de la Aplicación FastAPI

Este es el archivo principal que arranca la aplicación.
Configura FastAPI, middlewares, CORS, y registra los routers.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import time
import logging

from app.core.config import settings
from app.core.database import check_db_connection

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================
# Crear Instancia de FastAPI
# ============================================================

app = FastAPI(
    title=settings.project_name,
    description=settings.description,
    version=settings.version,
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
)


# ============================================================
# Configurar CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)


# ============================================================
# Middleware de Logging de Requests
# ============================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware que loguea cada request HTTP.

    Registra:
    - Método HTTP y path
    - Tiempo de procesamiento
    - Status code de respuesta
    """
    start_time = time.time()

    # Procesar el request
    response = await call_next(request)

    # Calcular tiempo de procesamiento
    process_time = time.time() - start_time

    # Loguear
    logger.info(
        f"{request.method} {request.url.path} "
        f"- Status: {response.status_code} "
        f"- Time: {process_time:.3f}s"
    )

    # Agregar header custom con tiempo de procesamiento
    response.headers["X-Process-Time"] = str(process_time)

    return response


# ============================================================
# Exception Handlers Globales
# ============================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler para errores de validación de Pydantic.

    Retorna un JSON amigable con los errores de validación.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })

    logger.warning(f"Validation error en {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Error de validación",
            "errors": errors
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handler para errores de SQLAlchemy (base de datos).

    En producción, no exponer detalles del error de DB.
    """
    logger.error(f"Database error en {request.url.path}: {exc}")

    if settings.environment == "production":
        error_detail = "Error interno del servidor"
    else:
        error_detail = str(exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": error_detail,
            "type": "database_error"
        }
    )


# ============================================================
# Eventos de Inicio y Cierre
# ============================================================

@app.on_event("startup")
async def startup_event():
    """
    Evento que se ejecuta al iniciar la aplicación.

    Verifica:
    - Conexión a la base de datos
    - Conexión a Redis (cuando se implemente)
    """
    logger.info("=" * 60)
    logger.info(f"Iniciando {settings.project_name} v{settings.version}")
    logger.info(f"Entorno: {settings.environment}")
    logger.info("=" * 60)

    # Verificar conexión a base de datos
    if check_db_connection():
        logger.info("✓ Conexión a PostgreSQL exitosa")
    else:
        logger.error("✗ No se pudo conectar a PostgreSQL")
        # En producción, podríamos querer terminar la app aquí
        if settings.environment == "production":
            raise Exception("Fallo crítico: No hay conexión a base de datos")

    logger.info(f"✓ Servidor escuchando en http://0.0.0.0:8000")
    logger.info(f"✓ Documentación disponible en http://localhost:8000{settings.api_v1_prefix}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento que se ejecuta al cerrar la aplicación.

    Limpia recursos y cierra conexiones.
    """
    logger.info("Cerrando aplicación...")
    # Aquí podríamos cerrar conexiones a Redis, pools de threads, etc.
    logger.info("✓ Aplicación cerrada correctamente")


# ============================================================
# Endpoints de Health Check
# ============================================================

@app.get(
    f"{settings.api_v1_prefix}/health",
    tags=["Health"],
    summary="Health Check",
    description="Endpoint para verificar que el servidor está funcionando"
)
async def health_check():
    """
    Health check básico.

    Returns:
        dict: Estado del servidor y servicios
    """
    db_status = "healthy" if check_db_connection() else "unhealthy"

    return {
        "status": "online",
        "environment": settings.environment,
        "version": settings.version,
        "services": {
            "database": db_status,
            "redis": "pending"  # TODO: Implementar check de Redis
        }
    }


@app.get(
    "/",
    tags=["Root"],
    summary="Root Endpoint",
    description="Redirige a la documentación de la API"
)
async def root():
    """
    Endpoint raíz que da información básica de la API.
    """
    return {
        "message": f"Bienvenido a {settings.project_name}",
        "version": settings.version,
        "docs": f"{settings.api_v1_prefix}/docs",
        "health": f"{settings.api_v1_prefix}/health"
    }


# ============================================================
# Registrar Routers (API v1)
# ============================================================

from app.api.v1 import auth, devices, readings

# Auth endpoints (login, logout, me)
app.include_router(
    auth.router,
    prefix=settings.api_v1_prefix
)

# Device endpoints (CRUD + schema)
app.include_router(
    devices.router,
    prefix=settings.api_v1_prefix
)

# Sensor readings endpoints (POST desde ESP32, GET con filtros)
app.include_router(
    readings.router,
    prefix=settings.api_v1_prefix
)

# TODO: Agregar mas routers a medida que se crean
# from app.api.v1 import users, locations, assets, alerts
#
# app.include_router(users.router, prefix=settings.api_v1_prefix)
# app.include_router(locations.router, prefix=settings.api_v1_prefix)
# app.include_router(assets.router, prefix=settings.api_v1_prefix)
# app.include_router(alerts.router, prefix=settings.api_v1_prefix)


# ============================================================
# Entry Point para Ejecución Directa (Desarrollo)
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Hot reload en desarrollo
        log_level=settings.log_level.lower()
    )
