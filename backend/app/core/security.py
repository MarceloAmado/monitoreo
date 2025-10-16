"""
Sistema de Monitoreo IoT
Módulo de Seguridad y Autenticación

Maneja:
- Hashing de contraseñas con bcrypt
- Generación y verificación de tokens JWT
- Validación de API Keys para devices ESP32
"""

from datetime import datetime, timedelta
from typing import Optional
import hashlib

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# ============================================================
# Configuración de Bcrypt para Hashing de Contraseñas
# ============================================================

# Context de Passlib configurado para bcrypt
# deprecated="auto" permite migrar de algoritmos viejos si es necesario
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Cost factor (12 es un buen balance seguridad/performance)
)


# ============================================================
# Funciones de Hashing de Contraseñas
# ============================================================

def hash_password(password: str) -> str:
    """
    Genera un hash bcrypt de una contraseña en texto plano.

    Args:
        password (str): Contraseña en texto plano

    Returns:
        str: Hash bcrypt de la contraseña

    Example:
        ```python
        hashed = hash_password("mi_password_segura")
        # "$2b$12$..."
        ```

    Notas:
        - NUNCA almacenar contraseñas en texto plano
        - El hash bcrypt incluye el salt automáticamente
        - Cada hash es único incluso para la misma contraseña
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con un hash.

    Args:
        plain_password (str): Contraseña ingresada por el usuario
        hashed_password (str): Hash almacenado en la base de datos

    Returns:
        bool: True si la contraseña es correcta, False en caso contrario

    Example:
        ```python
        if verify_password(input_password, user.password_hash):
            print("Contraseña correcta")
        ```
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================
# Funciones JWT (JSON Web Tokens)
# ============================================================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT para autenticación de usuarios.

    Args:
        data (dict): Payload del token (ej: {"sub": user.email, "role": "admin"})
        expires_delta (Optional[timedelta]): Tiempo de expiración custom

    Returns:
        str: Token JWT firmado

    Example:
        ```python
        token = create_access_token(
            data={"sub": "admin@example.com", "role": "super_admin"}
        )
        # "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        ```

    Notas:
        - El token incluye automáticamente el campo "exp" (expiration)
        - Si no se especifica expires_delta, usa el valor por defecto de config
    """
    to_encode = data.copy()

    # Calcular tiempo de expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    # Agregar campos estándar JWT
    to_encode.update({
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at
    })

    # Firmar el token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un token JWT.

    Args:
        token (str): Token JWT a decodificar

    Returns:
        Optional[dict]: Payload del token si es válido, None si es inválido/expirado

    Example:
        ```python
        payload = decode_access_token(token)
        if payload:
            user_email = payload.get("sub")
        else:
            print("Token inválido o expirado")
        ```

    Notas:
        - Valida automáticamente la firma y la expiración
        - Retorna None si el token está expirado o tiene firma inválida
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        # Token inválido, expirado o firma incorrecta
        print(f"Error decodificando JWT: {e}")
        return None


# ============================================================
# API Keys para Devices ESP32
# ============================================================

def generate_device_api_key(device_eui: str) -> str:
    """
    Genera una API Key única para un device ESP32.

    La API Key se deriva del device_eui + un salt secreto del servidor.
    Esto permite validar keys sin almacenarlas en la DB.

    Args:
        device_eui (str): Identificador único del device (ej: "ESP32_LAB_001")

    Returns:
        str: API Key en formato hexadecimal

    Example:
        ```python
        api_key = generate_device_api_key("ESP32_LAB_001")
        # "a3f5b8c2d9e1f4a7..."
        ```

    Notas:
        - La API Key es determinística (mismo device_eui = misma key)
        - El salt secreto debe estar en las variables de entorno
        - Si se cambia el salt, todas las keys quedan inválidas
    """
    # Concatenar device_eui con el salt secreto
    data = f"{device_eui}{settings.device_api_key_salt}".encode("utf-8")

    # Generar hash SHA256
    hash_object = hashlib.sha256(data)
    api_key = hash_object.hexdigest()

    return api_key


def validate_device_api_key(device_eui: str, provided_api_key: str) -> bool:
    """
    Valida que la API Key proporcionada sea correcta para el device.

    Args:
        device_eui (str): Device EUI que se está autenticando
        provided_api_key (str): API Key enviada en el header X-API-Key

    Returns:
        bool: True si la API Key es válida, False en caso contrario

    Example:
        ```python
        if validate_device_api_key("ESP32_LAB_001", request_api_key):
            # Permitir el acceso
            pass
        else:
            raise HTTPException(status_code=401, detail="API Key inválida")
        ```

    Notas:
        - Usa constant-time comparison para evitar timing attacks
    """
    expected_api_key = generate_device_api_key(device_eui)

    # Comparación en tiempo constante (seguridad contra timing attacks)
    return hmac_compare(expected_api_key, provided_api_key)


def hmac_compare(a: str, b: str) -> bool:
    """
    Compara dos strings en tiempo constante (evita timing attacks).

    Args:
        a (str): Primer string
        b (str): Segundo string

    Returns:
        bool: True si son iguales, False en caso contrario

    Notas:
        - NUNCA usar `a == b` para comparar secretos
        - Esta función toma el mismo tiempo sin importar dónde esté la diferencia
    """
    if len(a) != len(b):
        return False

    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)

    return result == 0


# ============================================================
# Utilidades de Validación
# ============================================================

def is_strong_password(password: str) -> tuple[bool, str]:
    """
    Valida que una contraseña cumpla con los requisitos de seguridad.

    Requisitos:
    - Mínimo 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Al menos un carácter especial

    Args:
        password (str): Contraseña a validar

    Returns:
        tuple[bool, str]: (es_válida, mensaje_error)

    Example:
        ```python
        is_valid, error_msg = is_strong_password("Password123!")
        if not is_valid:
            return {"error": error_msg}
        ```
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"

    if not any(c.isupper() for c in password):
        return False, "La contraseña debe tener al menos una mayúscula"

    if not any(c.islower() for c in password):
        return False, "La contraseña debe tener al menos una minúscula"

    if not any(c.isdigit() for c in password):
        return False, "La contraseña debe tener al menos un número"

    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "La contraseña debe tener al menos un carácter especial"

    return True, ""
