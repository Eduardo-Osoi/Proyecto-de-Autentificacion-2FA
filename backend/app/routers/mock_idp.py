from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.services.mock_idp_service import ErrorIntercambioToken, emitir_codigo_autorizacion, intercambiar_codigo_por_token, obtener_userinfo

router = APIRouter(prefix="/mock-idp", tags=["proveedor-simulado"])


@router.get("/autorizar")
def autorizar(
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    state: str = Query(...),
    email_simulado: str = Query(...),
    nombre_simulado: str = Query(...),
    db: Session = Depends(get_db),
):
    # esto seria accounts.google.com en la vida real. como es un proveedor de
    # mentira para poder probar el flujo sin credenciales reales, el "login"
    # es nada mas lo que el usuario escribio en la pantalla del frontend.
    if client_id != settings.sso_client_id:
        raise HTTPException(status_code=400, detail="client_id desconocido")

    codigo = emitir_codigo_autorizacion(db, email_simulado, nombre_simulado, redirect_uri)
    return RedirectResponse(url=f"{redirect_uri}?code={codigo}&state={state}")


@router.post("/token")
def token(
    grant_type: str,
    code: str,
    redirect_uri: str,
    client_id: str,
    client_secret: str,
    db: Session = Depends(get_db),
):
    if grant_type != "authorization_code":
        raise HTTPException(status_code=400, detail="grant_type no soportado")

    try:
        access_token = intercambiar_codigo_por_token(db, code, client_id, client_secret, redirect_uri)
    except ErrorIntercambioToken as ex:
        raise HTTPException(status_code=400, detail=str(ex))

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/userinfo")
def userinfo(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Encabezado Authorization invalido")

    access_token = authorization.removeprefix("Bearer ")
    try:
        return obtener_userinfo(access_token)
    except ErrorIntercambioToken as ex:
        raise HTTPException(status_code=401, detail=str(ex))
