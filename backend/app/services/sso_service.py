from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import CuentaExterna, EstadoSso, Usuario
from app.security import generar_codigo_aleatorio, hashear_password

EXPIRACION_STATE_MINUTOS = 5


def crear_estado(db: Session) -> str:
    state = generar_codigo_aleatorio()
    db.add(EstadoSso(state=state, expira_en=datetime.utcnow() + timedelta(minutes=EXPIRACION_STATE_MINUTOS)))
    db.commit()
    return state


def validar_y_consumir_estado(db: Session, state: str) -> bool:
    registro = db.query(EstadoSso).filter(EstadoSso.state == state).first()
    if registro is None or registro.usado or registro.expira_en < datetime.utcnow():
        return False

    registro.usado = True
    db.commit()
    return True


def resolver_usuario_desde_sso(db: Session, proveedor: str, email_externo: str, nombre_externo: str) -> Usuario:
    # si ya inicio con este proveedor antes, reusar el vinculo
    vinculo = (
        db.query(CuentaExterna)
        .filter(CuentaExterna.proveedor == proveedor, CuentaExterna.id_externo == email_externo)
        .first()
    )
    if vinculo is not None:
        return vinculo.usuario

    usuario = db.query(Usuario).filter(Usuario.email == email_externo).first()
    if usuario is None:
        usuario = Usuario(
            nombre=nombre_externo,
            email=email_externo,
            password_hash=hashear_password(generar_codigo_aleatorio()),
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

    db.add(CuentaExterna(usuario_id=usuario.id, proveedor=proveedor, id_externo=email_externo, email_externo=email_externo))
    db.commit()

    return usuario
