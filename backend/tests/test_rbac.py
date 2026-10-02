from tests.conftest import encabezado_auth, registrar


def test_usuario_sin_rol_no_puede_crear_roles(client):
    registrar(client, email="ana@bastion.com")  # admin, primer usuario
    sesion_beto = registrar(client, nombre="Beto", email="beto@bastion.com")

    respuesta = client.post(
        "/api/roles", json={"nombre": "editor"}, headers=encabezado_auth(sesion_beto["token"])
    )
    assert respuesta.status_code == 403


def test_admin_puede_crear_rol_y_permiso_y_asignarlos(client):
    admin = registrar(client)
    headers = encabezado_auth(admin["token"])

    rol = client.post("/api/roles", json={"nombre": "editor", "descripcion": "Puede editar contenido"}, headers=headers).json()
    permiso = client.post("/api/permisos", json={"clave": "contenido:editar"}, headers=headers).json()

    respuesta = client.post(f"/api/roles/{rol['id']}/permisos/{permiso['id']}", headers=headers)
    assert respuesta.status_code == 200


def test_asignar_rol_a_usuario_le_da_sus_permisos_tras_refrescar(client):
    admin = registrar(client)
    headers_admin = encabezado_auth(admin["token"])
    beto = registrar(client, nombre="Beto", email="beto@bastion.com")

    rol = client.post("/api/roles", json={"nombre": "editor"}, headers=headers_admin).json()
    permiso = client.post("/api/permisos", json={"clave": "contenido:editar"}, headers=headers_admin).json()
    client.post(f"/api/roles/{rol['id']}/permisos/{permiso['id']}", headers=headers_admin)

    respuesta_asignacion = client.post(
        f"/api/usuarios/{beto['usuario_id']}/roles/{rol['id']}", headers=headers_admin
    )
    assert respuesta_asignacion.status_code == 200

    perfil_antes_de_refrescar = client.get("/api/auth/perfil", headers=encabezado_auth(beto["token"])).json()
    assert "contenido:editar" in perfil_antes_de_refrescar["permisos"]

    sesion_refrescada = client.post("/api/auth/refrescar", headers=encabezado_auth(beto["token"])).json()
    assert "contenido:editar" in sesion_refrescada["permisos"]


def test_demo_solo_admins_requiere_el_permiso_correcto(client):
    admin = registrar(client)
    beto = registrar(client, nombre="Beto", email="beto@bastion.com")

    respuesta_admin = client.get("/api/demo/solo-admins", headers=encabezado_auth(admin["token"]))
    assert respuesta_admin.status_code == 200

    respuesta_beto = client.get("/api/demo/solo-admins", headers=encabezado_auth(beto["token"]))
    assert respuesta_beto.status_code == 403


def test_no_se_puede_crear_un_rol_con_nombre_repetido(client):
    admin = registrar(client)
    headers = encabezado_auth(admin["token"])
    client.post("/api/roles", json={"nombre": "editor"}, headers=headers)
    respuesta = client.post("/api/roles", json={"nombre": "editor"}, headers=headers)
    assert respuesta.status_code == 400


def test_quitar_rol_revoca_el_permiso_tras_refrescar(client):
    admin = registrar(client)
    headers_admin = encabezado_auth(admin["token"])
    beto = registrar(client, nombre="Beto", email="beto@bastion.com")

    rol = client.post("/api/roles", json={"nombre": "editor"}, headers=headers_admin).json()
    permiso = client.post("/api/permisos", json={"clave": "contenido:editar"}, headers=headers_admin).json()
    client.post(f"/api/roles/{rol['id']}/permisos/{permiso['id']}", headers=headers_admin)
    client.post(f"/api/usuarios/{beto['usuario_id']}/roles/{rol['id']}", headers=headers_admin)

    client.delete(f"/api/usuarios/{beto['usuario_id']}/roles/{rol['id']}", headers=headers_admin)

    sesion_refrescada = client.post("/api/auth/refrescar", headers=encabezado_auth(beto["token"])).json()
    assert "contenido:editar" not in sesion_refrescada["permisos"]


def test_listar_usuarios_requiere_permiso_de_administracion(client):
    admin = registrar(client)
    beto = registrar(client, nombre="Beto", email="beto@bastion.com")

    respuesta_beto = client.get("/api/usuarios", headers=encabezado_auth(beto["token"]))
    assert respuesta_beto.status_code == 403

    respuesta_admin = client.get("/api/usuarios", headers=encabezado_auth(admin["token"]))
    assert respuesta_admin.status_code == 200
    assert len(respuesta_admin.json()) == 2
