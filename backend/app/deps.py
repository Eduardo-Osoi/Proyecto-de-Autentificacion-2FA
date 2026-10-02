from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.security import decodificar_token_sesion

bearer_scheme = HTTPBearer()


class UsuarioAutenticado:
    def __init__(self, usuario_id: int, nombre: str, roles: list[str], permisos: list[str]):
        self.id = usuario_id
        self.nombre = nombre
        self.roles = roles
        self.permisos = permisos


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UsuarioAutenticado:
    try:
        payload = decodificar_token_sesion(credenciales.credentials)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido o expirado")

    return UsuarioAutenticado(
        usuario_id=int(payload["sub"]),
        nombre=payload.get("nombre", ""),
        roles=payload.get("roles", []),
        permisos=payload.get("permisos", []),
    )


def requerir_permiso(clave_permiso: str):
    # se usa asi: Depends(requerir_permiso("usuarios:administrar"))
    def verificador(usuario: UsuarioAutenticado = Depends(obtener_usuario_actual)) -> UsuarioAutenticado:
        if clave_permiso not in usuario.permisos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requiere el permiso '{clave_permiso}'",
            )
        return usuario

    return verificador


def obtener_usuario_db(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario
