import secrets
from datetime import datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from app.config import settings

_hasher = PasswordHasher()


def hashear_password(password: str) -> str:
    return _hasher.hash(password)


def verificar_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def generar_token_sesion(usuario_id: int, nombre: str, roles: list[str], permisos: list[str]) -> str:
    expira = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    payload = {
        "sub": str(usuario_id),
        "nombre": nombre,
        "roles": roles,
        "permisos": permisos,
        "exp": expira,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decodificar_token_sesion(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as ex:
        raise ValueError("Token invalido o expirado") from ex


def generar_codigo_aleatorio(longitud: int = 32) -> str:
    return secrets.token_urlsafe(longitud)
