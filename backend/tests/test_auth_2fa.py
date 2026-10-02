from app.services.totp_service import totp
from tests.conftest import encabezado_auth, registrar


def test_el_primer_usuario_registrado_es_administrador(client):
    sesion = registrar(client)
    assert "admin" in sesion["roles"]
    assert "roles:administrar" in sesion["permisos"]
    assert "admin:acceso" in sesion["permisos"]


def test_el_segundo_usuario_no_recibe_rol_de_administrador(client):
    registrar(client, email="ana@bastion.com")
    sesion_2 = registrar(client, nombre="Beto", email="beto@bastion.com")
    assert sesion_2["roles"] == []
    assert sesion_2["permisos"] == []


def test_no_se_puede_registrar_el_mismo_correo_dos_veces(client):
    registrar(client)
    respuesta = client.post(
        "/api/auth/registro", json={"nombre": "Otra Ana", "email": "ana@bastion.com", "password": "otraclave123"}
    )
    assert respuesta.status_code == 400


def test_login_exitoso_sin_2fa_devuelve_sesion_directamente(client):
    registrar(client)
    respuesta = client.post("/api/auth/login", json={"email": "ana@bastion.com", "password": "clave12345"})
    assert respuesta.status_code == 200
    assert "token" in respuesta.json()


def test_login_con_password_incorrecto_falla(client):
    registrar(client)
    respuesta = client.post("/api/auth/login", json={"email": "ana@bastion.com", "password": "incorrecta"})
    assert respuesta.status_code == 401


def test_password_no_se_guarda_en_texto_plano(client, test_engine):
    registrar(client)
    with test_engine.connect() as conexion:
        fila = conexion.exec_driver_sql("SELECT password_hash FROM usuarios WHERE email = 'ana@bastion.com'").fetchone()
    assert fila[0] != "clave12345"
    assert fila[0].startswith("$argon2")


def test_flujo_completo_de_activacion_y_login_con_2fa(client):
    sesion = registrar(client)
    headers = encabezado_auth(sesion["token"])

    configuracion = client.post("/api/2fa/iniciar-configuracion", headers=headers).json()
    secreto = configuracion["secreto"]

    codigo_valido = totp(secreto)
    confirmacion = client.post("/api/2fa/confirmar", json={"codigo": codigo_valido}, headers=headers)
    assert confirmacion.status_code == 200
    assert confirmacion.json()["totp_habilitado"] is True

    respuesta_login = client.post("/api/auth/login", json={"email": "ana@bastion.com", "password": "clave12345"})
    assert respuesta_login.status_code == 200
    cuerpo_login = respuesta_login.json()
    assert cuerpo_login["requiere_2fa"] is True
    login_token = cuerpo_login["login_token"]

    codigo_segundo_factor = totp(secreto)
    respuesta_2fa = client.post("/api/auth/login/2fa", json={"login_token": login_token, "codigo": codigo_segundo_factor})
    assert respuesta_2fa.status_code == 200
    assert "token" in respuesta_2fa.json()


def test_confirmar_2fa_con_codigo_incorrecto_no_lo_habilita(client):
    sesion = registrar(client)
    headers = encabezado_auth(sesion["token"])
    client.post("/api/2fa/iniciar-configuracion", headers=headers)

    respuesta = client.post("/api/2fa/confirmar", json={"codigo": "000000"}, headers=headers)
    assert respuesta.status_code == 400

    perfil = client.get("/api/auth/perfil", headers=headers).json()
    assert perfil["totp_habilitado"] is False


def test_login_temporal_no_se_puede_reutilizar(client):
    sesion = registrar(client)
    headers = encabezado_auth(sesion["token"])
    configuracion = client.post("/api/2fa/iniciar-configuracion", headers=headers).json()
    secreto = configuracion["secreto"]
    client.post("/api/2fa/confirmar", json={"codigo": totp(secreto)}, headers=headers)

    login_token = client.post(
        "/api/auth/login", json={"email": "ana@bastion.com", "password": "clave12345"}
    ).json()["login_token"]

    primer_intento = client.post(
        "/api/auth/login/2fa", json={"login_token": login_token, "codigo": totp(secreto)}
    )
    assert primer_intento.status_code == 200

    segundo_intento = client.post(
        "/api/auth/login/2fa", json={"login_token": login_token, "codigo": totp(secreto)}
    )
    assert segundo_intento.status_code == 401


def test_deshabilitar_2fa_permite_login_directo_de_nuevo(client):
    sesion = registrar(client)
    headers = encabezado_auth(sesion["token"])
    configuracion = client.post("/api/2fa/iniciar-configuracion", headers=headers).json()
    client.post("/api/2fa/confirmar", json={"codigo": totp(configuracion["secreto"])}, headers=headers)

    client.post("/api/2fa/deshabilitar", headers=headers)

    respuesta = client.post("/api/auth/login", json={"email": "ana@bastion.com", "password": "clave12345"})
    assert "token" in respuesta.json()


def test_endpoint_protegido_sin_token_da_401_o_403(client):
    respuesta = client.get("/api/auth/perfil")
    assert respuesta.status_code in (401, 403)
