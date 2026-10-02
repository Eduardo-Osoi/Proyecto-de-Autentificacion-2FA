from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import UsuarioAutenticado, obtener_usuario_actual, obtener_usuario_db
from app.schemas.schemas import (
    Login2faEntrada,
    LoginEntrada,
    PerfilRespuesta,
    RegistroEntrada,
    RequiereSegundoFactorRespuesta,
    SesionRespuesta,
)
from app.services.auth_service import (
    autenticar_con_password,
    consumir_login_temporal,
    crear_login_temporal,
    emitir_sesion,
    registrar_usuario,
)
from app.services.totp_service import verificar_codigo

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/registro", response_model=SesionRespuesta)
def registro(entrada: RegistroEntrada, db: Session = Depends(get_db)):
    from app.models import Usuario

    if db.query(Usuario).filter(Usuario.email == entrada.email).first():
        raise HTTPException(status_code=400, detail="Ya existe una cuenta con ese correo")

    usuario = registrar_usuario(db, entrada.nombre, entrada.email, entrada.password)
    return emitir_sesion(usuario)


@router.post("/login", response_model=SesionRespuesta | RequiereSegundoFactorRespuesta)
def login(entrada: LoginEntrada, db: Session = Depends(get_db)):
    usuario = autenticar_con_password(db, entrada.email, entrada.password)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    if usuario.totp_habilitado:
        login_token = crear_login_temporal(db, usuario.id)
        return RequiereSegundoFactorRespuesta(login_token=login_token)

    return emitir_sesion(usuario)


@router.post("/login/2fa", response_model=SesionRespuesta)
def login_2fa(entrada: Login2faEntrada, db: Session = Depends(get_db)):
    registro_temporal = consumir_login_temporal(db, entrada.login_token)
    if registro_temporal is None:
        raise HTTPException(status_code=401, detail="El login temporal es invalido o expiro, inicia sesion de nuevo")

    from app.models import Usuario

    usuario = db.get(Usuario, registro_temporal.usuario_id)
    if usuario is None or not usuario.totp_secreto:
        raise HTTPException(status_code=401, detail="No se pudo completar el segundo factor")

    if not verificar_codigo(usuario.totp_secreto, entrada.codigo):
        raise HTTPException(status_code=401, detail="Codigo de verificacion incorrecto")

    return emitir_sesion(usuario)


@router.get("/perfil", response_model=PerfilRespuesta)
def perfil(db: Session = Depends(get_db), usuario_actual: UsuarioAutenticado = Depends(obtener_usuario_actual)):
    usuario = obtener_usuario_db(db, usuario_actual.id)
    return PerfilRespuesta(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        roles=usuario.nombres_roles(),
        permisos=sorted(usuario.permisos_efectivos()),
        totp_habilitado=usuario.totp_habilitado,
    )


@router.post("/refrescar", response_model=SesionRespuesta)
def refrescar(db: Session = Depends(get_db), usuario_actual: UsuarioAutenticado = Depends(obtener_usuario_actual)):
    # los permisos van dentro del JWT para no consultar la bd en cada request,
    # pero eso implica que si te cambian de rol, tu token viejo no se entera
    # hasta que vuelvas a loguearte o pegues aqui.
    usuario = obtener_usuario_db(db, usuario_actual.id)
    return emitir_sesion(usuario)
