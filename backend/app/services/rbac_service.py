from sqlalchemy.orm import Session

from app.models import Permiso, Rol, Usuario


def crear_rol(db: Session, nombre: str, descripcion: str | None) -> Rol:
    rol = Rol(nombre=nombre, descripcion=descripcion)
    db.add(rol)
    db.commit()
    db.refresh(rol)
    return rol


def crear_permiso(db: Session, clave: str, descripcion: str | None) -> Permiso:
    permiso = Permiso(clave=clave, descripcion=descripcion)
    db.add(permiso)
    db.commit()
    db.refresh(permiso)
    return permiso


def asignar_permiso_a_rol(db: Session, rol: Rol, permiso: Permiso) -> Rol:
    if permiso not in rol.permisos:
        rol.permisos.append(permiso)
        db.commit()
        db.refresh(rol)
    return rol


def asignar_rol_a_usuario(db: Session, usuario: Usuario, rol: Rol) -> Usuario:
    if rol not in usuario.roles:
        usuario.roles.append(rol)
        db.commit()
        db.refresh(usuario)
    return usuario


def quitar_rol_a_usuario(db: Session, usuario: Usuario, rol: Rol) -> Usuario:
    if rol in usuario.roles:
        usuario.roles.remove(rol)
        db.commit()
        db.refresh(usuario)
    return usuario
