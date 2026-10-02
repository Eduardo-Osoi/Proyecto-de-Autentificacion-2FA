from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.models import LoginTemporal, Permiso, Rol, Usuario
from app.security import generar_codigo_aleatorio, generar_token_sesion, hashear_password, verificar_password
from app.services import totp_service

PERMISOS_BASE_ADMIN = [
    ("admin:acceso", "Acceso al panel de administracion"),
    ("roles:administrar", "Crear/editar roles y permisos"),
    ("usuarios:administrar", "Ver usuarios y asignarles roles"),
]


def _crear_admin_inicial(db: Session, usuario: Usuario) -> None:
    # se ejecuta solo la primera vez: si no hay nadie con permiso para crear roles,
    # nadie podria crear el primer rol nunca. asi que el primer registro = admin.
    rol_admin = db.query(Rol).filter(Rol.nombre == "admin").first()
    if rol_admin is None:
        rol_admin = Rol(nombre="admin", descripcion="Administrador con acceso total")
        db.add(rol_admin)
        db.flush()

    for clave, descripcion in PERMISOS_BASE_ADMIN:
        permiso = db.query(Permiso).filter(Permiso.clave == clave).first()
        if permiso is None:
            permiso = Permiso(clave=clave, descripcion=descripcion)
            db.add(permiso)
            db.flush()
        if permiso not in rol_admin.permisos:
            rol_admin.permisos.append(permiso)

    usuario.roles.append(rol_admin)
    db.commit()


def registrar_usuario(db: Session, nombre: str, email: str, password: str) -> Usuario:
    es_primer_usuario = db.query(Usuario).count() == 0

    usuario = Usuario(nombre=nombre, email=email, password_hash=hashear_password(password))
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    if es_primer_usuario:
        _crear_admin_inicial(db, usuario)
        db.refresh(usuario)

    return usuario


def emitir_sesion(usuario: Usuario) -> dict:
    roles = usuario.nombres_roles()
    permisos = sorted(usuario.permisos_efectivos())
    token = generar_token_sesion(usuario.id, usuario.nombre, roles, permisos)
    return {"token": token, "usuario_id": usuario.id, "nombre": usuario.nombre, "roles": roles, "permisos": permisos}


def crear_login_temporal(db: Session, usuario_id: int) -> str:
    token = generar_codigo_aleatorio()
    expira_en = datetime.utcnow() + timedelta(minutes=settings.login_temporal_expiration_minutes)
    db.add(LoginTemporal(token=token, usuario_id=usuario_id, expira_en=expira_en))
    db.commit()
    return token


def consumir_login_temporal(db: Session, token: str) -> LoginTemporal | None:
    registro = db.query(LoginTemporal).filter(LoginTemporal.token == token).first()
    if registro is None or registro.usado or registro.expira_en < datetime.utcnow():
        return None

    registro.usado = True
    db.commit()
    return registro


def autenticar_con_password(db: Session, email: str, password: str) -> Usuario | None:
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario is None or not verificar_password(password, usuario.password_hash):
        return None
    return usuario


def habilitar_2fa(db: Session, usuario: Usuario) -> tuple[str, str]:
    secreto = totp_service.generar_secreto()
    usuario.totp_secreto = secreto
    db.commit()

    uri = totp_service.generar_uri_otpauth(secreto, usuario.email, settings.emisor_totp)
    return secreto, uri


def confirmar_2fa(usuario: Usuario, codigo: str, db: Session) -> bool:
    if not usuario.totp_secreto:
        return False
    if not totp_service.verificar_codigo(usuario.totp_secreto, codigo):
        return False

    usuario.totp_habilitado = True
    db.commit()
    return True


def deshabilitar_2fa(usuario: Usuario, db: Session) -> None:
    usuario.totp_habilitado = False
    usuario.totp_secreto = None
    db.commit()
