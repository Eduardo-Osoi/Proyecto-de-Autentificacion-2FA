from fastapi import APIRouter, Depends

from app.deps import UsuarioAutenticado, requerir_permiso

router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.get("/solo-admins")
def solo_admins(usuario: UsuarioAutenticado = Depends(requerir_permiso("admin:acceso"))):
    return {"mensaje": f"Hola {usuario.nombre}, tienes el permiso 'admin:acceso'."}
