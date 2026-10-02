from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import UsuarioAutenticado, requerir_permiso
from app.models import Permiso, Rol, Usuario
from app.schemas.schemas import (
    CrearPermisoEntrada,
    CrearRolEntrada,
    PermisoRespuesta,
    RolRespuesta,
    UsuarioAdminRespuesta,
)
from app.services.rbac_service import asignar_permiso_a_rol, asignar_rol_a_usuario, crear_permiso, crear_rol, quitar_rol_a_usuario

router = APIRouter(prefix="/api", tags=["rbac"])


def _obtener_o_404(db: Session, modelo, id_: int, nombre_entidad: str):
    instancia = db.get(modelo, id_)
    if instancia is None:
        raise HTTPException(status_code=404, detail=f"{nombre_entidad} no encontrado")
    return instancia


@router.post("/roles", response_model=RolRespuesta)
def crear(
    entrada: CrearRolEntrada,
    db: Session = Depends(get_db),
    _usuario: UsuarioAutenticado = Depends(requerir_permiso("roles:administrar")),
):
    if db.query(Rol).filter(Rol.nombre == entrada.nombre).first():
        raise HTTPException(status_code=400, detail="Ya existe un rol con ese nombre")
    return crear_rol(db, entrada.nombre, entrada.descripcion)


@router.get("/roles", response_model=List[RolRespuesta])
def listar_roles(db: Session = Depends(get_db)):
    return db.query(Rol).all()


@router.post("/permisos", response_model=PermisoRespuesta)
def crear_permiso_endpoint(
    entrada: CrearPermisoEntrada,
    db: Session = Depends(get_db),
    _usuario: UsuarioAutenticado = Depends(requerir_permiso("roles:administrar")),
):
    if db.query(Permiso).filter(Permiso.clave == entrada.clave).first():
        raise HTTPException(status_code=400, detail="Ya existe un permiso con esa clave")
    return crear_permiso(db, entrada.clave, entrada.descripcion)


@router.get("/permisos", response_model=List[PermisoRespuesta])
def listar_permisos(db: Session = Depends(get_db)):
    return db.query(Permiso).all()


@router.post("/roles/{rol_id}/permisos/{permiso_id}", response_model=RolRespuesta)
def asignar_permiso(
    rol_id: int,
    permiso_id: int,
    db: Session = Depends(get_db),
    _usuario: UsuarioAutenticado = Depends(requerir_permiso("roles:administrar")),
):
    rol = _obtener_o_404(db, Rol, rol_id, "Rol")
    permiso = _obtener_o_404(db, Permiso, permiso_id, "Permiso")
    return asignar_permiso_a_rol(db, rol, permiso)


@router.get("/usuarios", response_model=List[UsuarioAdminRespuesta])
def listar_usuarios(
    db: Session = Depends(get_db),
    _usuario: UsuarioAutenticado = Depends(requerir_permiso("usuarios:administrar")),
):
    usuarios = db.query(Usuario).all()
    return [
        UsuarioAdminRespuesta(
            id=u.id,
            nombre=u.nombre,
            email=u.email,
            roles=u.nombres_roles(),
            totp_habilitado=u.totp_habilitado,
            creado_en=u.creado_en,
        )
        for u in usuarios
    ]


@router.post("/usuarios/{usuario_id}/roles/{rol_id}")
def asignar_rol(
    usuario_id: int,
    rol_id: int,
    db: Session = Depends(get_db),
    _usuario: UsuarioAutenticado = Depends(requerir_permiso("usuarios:administrar")),
):
    usuario = _obtener_o_404(db, Usuario, usuario_id, "Usuario")
    rol = _obtener_o_404(db, Rol, rol_id, "Rol")
    asignar_rol_a_usuario(db, usuario, rol)
    return {"ok": True}


@router.delete("/usuarios/{usuario_id}/roles/{rol_id}")
def quitar_rol(
    usuario_id: int,
    rol_id: int,
    db: Session = Depends(get_db),
    _usuario: UsuarioAutenticado = Depends(requerir_permiso("usuarios:administrar")),
):
    usuario = _obtener_o_404(db, Usuario, usuario_id, "Usuario")
    rol = _obtener_o_404(db, Rol, rol_id, "Rol")
    quitar_rol_a_usuario(db, usuario, rol)
    return {"ok": True}
