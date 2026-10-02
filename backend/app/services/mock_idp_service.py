from datetime import datetime, timedelta

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models import CodigoAutorizacionSso
from app.security import generar_codigo_aleatorio

EXPIRACION_CODIGO_MINUTOS = 5
EXPIRACION_ACCESS_TOKEN_MINUTOS = 10
SECRETO_PROVEEDOR = settings.jwt_secret + "::mock-idp"  # namespace distinto al JWT de sesion de Bastion


def emitir_codigo_autorizacion(db: Session, email_simulado: str, nombre_simulado: str, redirect_uri: str) -> str:
    codigo = generar_codigo_aleatorio()
    expira_en = datetime.utcnow() + timedelta(minutes=EXPIRACION_CODIGO_MINUTOS)

    db.add(
        CodigoAutorizacionSso(
            codigo=codigo,
            email_simulado=email_simulado,
            nombre_simulado=nombre_simulado,
            redirect_uri=redirect_uri,
            expira_en=expira_en,
        )
    )
    db.commit()
    return codigo


class ErrorIntercambioToken(Exception):
    pass


def intercambiar_codigo_por_token(db: Session, codigo: str, client_id: str, client_secret: str, redirect_uri: str) -> str:
    if client_id != settings.sso_client_id or client_secret != settings.sso_client_secret:
        raise ErrorIntercambioToken("client_id o client_secret invalidos")

    registro = db.query(CodigoAutorizacionSso).filter(CodigoAutorizacionSso.codigo == codigo).first()

    if registro is None or registro.usado or registro.expira_en < datetime.utcnow():
        raise ErrorIntercambioToken("Codigo de autorizacion invalido, usado o expirado")

    if registro.redirect_uri != redirect_uri:
        raise ErrorIntercambioToken("redirect_uri no coincide con la solicitada al autorizar")

    registro.usado = True
    db.commit()

    expira = datetime.utcnow() + timedelta(minutes=EXPIRACION_ACCESS_TOKEN_MINUTOS)
    payload = {"email": registro.email_simulado, "nombre": registro.nombre_simulado, "exp": expira}
    return jwt.encode(payload, SECRETO_PROVEEDOR, algorithm="HS256")


def obtener_userinfo(access_token: str) -> dict:
    try:
        payload = jwt.decode(access_token, SECRETO_PROVEEDOR, algorithms=["HS256"])
    except JWTError as ex:
        raise ErrorIntercambioToken("Access token invalido o expirado") from ex

    return {"email": payload["email"], "nombre": payload["nombre"]}
