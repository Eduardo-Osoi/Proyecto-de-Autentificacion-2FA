from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.database import Base

usuario_rol = Table(
    "usuario_rol",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("usuarios.id"), primary_key=True),
    Column("rol_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

rol_permiso = Table(
    "rol_permiso",
    Base.metadata,
    Column("rol_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permiso_id", Integer, ForeignKey("permisos.id"), primary_key=True),
)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)

    totp_secreto = Column(String, nullable=True)
    totp_habilitado = Column(Boolean, nullable=False, default=False)

    creado_en = Column(DateTime, default=datetime.utcnow)

    roles = relationship("Rol", secondary=usuario_rol, back_populates="usuarios")
    cuentas_externas = relationship("CuentaExterna", back_populates="usuario")

    def permisos_efectivos(self) -> set[str]:
        claves = set()
        for rol in self.roles:
            for permiso in rol.permisos:
                claves.add(permiso.clave)
        return claves

    def nombres_roles(self) -> list[str]:
        return [rol.nombre for rol in self.roles]


class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)
    descripcion = Column(String, nullable=True)

    usuarios = relationship("Usuario", secondary=usuario_rol, back_populates="roles")
    permisos = relationship("Permiso", secondary=rol_permiso, back_populates="roles")


class Permiso(Base):
    __tablename__ = "permisos"

    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String, nullable=False, unique=True)  # ej. "facturas:crear"
    descripcion = Column(String, nullable=True)

    roles = relationship("Rol", secondary=rol_permiso, back_populates="permisos")


class CuentaExterna(Base):
    # vincula un usuario local con su identidad en un proveedor SSO externo
    __tablename__ = "cuentas_externas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    proveedor = Column(String, nullable=False)
    id_externo = Column(String, nullable=False)
    email_externo = Column(String, nullable=False)

    usuario = relationship("Usuario", back_populates="cuentas_externas")


class LoginTemporal(Base):
    # token de corta duracion mientras esperamos el codigo TOTP en el login.
    # no es sesion, solo sirve para completar el segundo factor.
    __tablename__ = "logins_temporales"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False, unique=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    expira_en = Column(DateTime, nullable=False)
    usado = Column(Boolean, nullable=False, default=False)


class CodigoAutorizacionSso(Base):
    # codigo de un solo uso que emite el proveedor simulado
    __tablename__ = "codigos_autorizacion_sso"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, nullable=False, unique=True, index=True)
    email_simulado = Column(String, nullable=False)
    nombre_simulado = Column(String, nullable=False)
    redirect_uri = Column(String, nullable=False)
    expira_en = Column(DateTime, nullable=False)
    usado = Column(Boolean, nullable=False, default=False)


class EstadoSso(Base):
    # el "state" de OAuth2: se genera antes de mandar al usuario al proveedor
    # y se checa al volver, para que nadie meta su propio "code" en tu callback
    __tablename__ = "estados_sso"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, nullable=False, unique=True, index=True)
    expira_en = Column(DateTime, nullable=False)
    usado = Column(Boolean, nullable=False, default=False)
