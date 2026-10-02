from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import UsuarioAutenticado, obtener_usuario_actual, obtener_usuario_db
from app.schemas.schemas import Configuracion2faRespuesta, Confirmar2faEntrada
from app.services.auth_service import confirmar_2fa, deshabilitar_2fa, habilitar_2fa

router = APIRouter(prefix="/api/2fa", tags=["2fa"])


@router.post("/iniciar-configuracion", response_model=Configuracion2faRespuesta)
def iniciar_configuracion(
    db: Session = Depends(get_db), usuario_actual: UsuarioAutenticado = Depends(obtener_usuario_actual)
):
    usuario = obtener_usuario_db(db, usuario_actual.id)
    secreto, uri = habilitar_2fa(db, usuario)
    return Configuracion2faRespuesta(secreto=secreto, uri_otpauth=uri)


@router.post("/confirmar")
def confirmar(
    entrada: Confirmar2faEntrada,
    db: Session = Depends(get_db),
    usuario_actual: UsuarioAutenticado = Depends(obtener_usuario_actual),
):
    usuario = obtener_usuario_db(db, usuario_actual.id)
    if not confirmar_2fa(usuario, entrada.codigo, db):
        raise HTTPException(status_code=400, detail="Codigo incorrecto, intenta de nuevo")
    return {"totp_habilitado": True}


@router.post("/deshabilitar")
def deshabilitar(
    db: Session = Depends(get_db), usuario_actual: UsuarioAutenticado = Depends(obtener_usuario_actual)
):
    usuario = obtener_usuario_db(db, usuario_actual.id)
    deshabilitar_2fa(usuario, db)
    return {"totp_habilitado": False}
