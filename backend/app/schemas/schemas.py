from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class RegistroEntrada(BaseModel):
    nombre: str
    email: EmailStr
    password: str = Field(min_length=8)


class LoginEntrada(BaseModel):
    email: EmailStr
    password: str


class Login2faEntrada(BaseModel):
    login_token: str
    codigo: str


class SesionRespuesta(BaseModel):
    token: str
    usuario_id: int
    nombre: str
    roles: List[str]
    permisos: List[str]


class RequiereSegundoFactorRespuesta(BaseModel):
    requiere_2fa: bool = True
    login_token: str


class Confirmar2faEntrada(BaseModel):
    codigo: str


class Configuracion2faRespuesta(BaseModel):
    secreto: str
    uri_otpauth: str


class PerfilRespuesta(BaseModel):
    id: int
    nombre: str
    email: str
    roles: List[str]
    permisos: List[str]
    totp_habilitado: bool


class CrearRolEntrada(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class RolRespuesta(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]

    class Config:
        from_attributes = True


class CrearPermisoEntrada(BaseModel):
    clave: str
    descripcion: Optional[str] = None


class PermisoRespuesta(BaseModel):
    id: int
    clave: str
    descripcion: Optional[str]

    class Config:
        from_attributes = True


class UsuarioAdminRespuesta(BaseModel):
    id: int
    nombre: str
    email: str
    roles: List[str]
    totp_habilitado: bool
    creado_en: datetime

    class Config:
        from_attributes = True
