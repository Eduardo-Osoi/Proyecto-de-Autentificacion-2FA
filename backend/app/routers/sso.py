from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.services.auth_service import emitir_sesion
from app.services.mock_idp_service import ErrorIntercambioToken, intercambiar_codigo_por_token, obtener_userinfo
from app.services.sso_service import crear_estado, resolver_usuario_desde_sso, validar_y_consumir_estado

router = APIRouter(prefix="/api/sso", tags=["sso"])

CALLBACK_PATH = "/api/sso/callback"


@router.get("/iniciar")
def iniciar(db: Session = Depends(get_db)):
    state = crear_estado(db)
    redirect_uri = f"{settings.backend_base_url}{CALLBACK_PATH}"

    url_pantalla_proveedor = (
        f"{settings.frontend_base_url}/sso/proveedor-simulado"
        f"?client_id={settings.sso_client_id}&redirect_uri={redirect_uri}&state={state}"
    )
    return {"url_autorizacion": url_pantalla_proveedor}


@router.get("/callback")
def callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    if not validar_y_consumir_estado(db, state):
        raise HTTPException(status_code=400, detail="Parametro state invalido, expirado o ya usado (posible CSRF)")

    redirect_uri = f"{settings.backend_base_url}{CALLBACK_PATH}"

    try:
        access_token = intercambiar_codigo_por_token(
            db, code, settings.sso_client_id, settings.sso_client_secret, redirect_uri
        )
        datos_usuario = obtener_userinfo(access_token)
    except ErrorIntercambioToken as ex:
        raise HTTPException(status_code=400, detail=str(ex))

    usuario = resolver_usuario_desde_sso(db, "proveedor-simulado", datos_usuario["email"], datos_usuario["nombre"])
    sesion = emitir_sesion(usuario)

    return RedirectResponse(url=f"{settings.frontend_base_url}/sso/completado?token={sesion['token']}")
