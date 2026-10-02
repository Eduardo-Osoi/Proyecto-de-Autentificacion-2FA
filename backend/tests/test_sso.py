from urllib.parse import parse_qs, urlparse

from tests.conftest import encabezado_auth, registrar


def _extraer_query(url: str) -> dict:
    return {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}


def test_flujo_sso_completo_crea_un_usuario_nuevo(client):
    respuesta_iniciar = client.get("/api/sso/iniciar")
    assert respuesta_iniciar.status_code == 200
    url_proveedor = respuesta_iniciar.json()["url_autorizacion"]
    parametros = _extraer_query(url_proveedor)

    respuesta_autorizar = client.get(
        "/mock-idp/autorizar",
        params={
            "client_id": parametros["client_id"],
            "redirect_uri": parametros["redirect_uri"],
            "state": parametros["state"],
            "email_simulado": "carla@externo.com",
            "nombre_simulado": "Carla Externa",
        },
    )
    assert respuesta_autorizar.status_code == 307
    parametros_callback = _extraer_query(respuesta_autorizar.headers["location"])
    assert parametros_callback["state"] == parametros["state"]

    respuesta_callback = client.get(
        "/api/sso/callback", params={"code": parametros_callback["code"], "state": parametros_callback["state"]}
    )
    assert respuesta_callback.status_code == 307
    assert "token=" in respuesta_callback.headers["location"]


def test_state_no_se_puede_reutilizar(client):
    parametros = _extraer_query(client.get("/api/sso/iniciar").json()["url_autorizacion"])

    respuesta_autorizar = client.get(
        "/mock-idp/autorizar",
        params={
            "client_id": parametros["client_id"],
            "redirect_uri": parametros["redirect_uri"],
            "state": parametros["state"],
            "email_simulado": "carla@externo.com",
            "nombre_simulado": "Carla Externa",
        },
    )
    parametros_callback = _extraer_query(respuesta_autorizar.headers["location"])

    client.get("/api/sso/callback", params={"code": parametros_callback["code"], "state": parametros_callback["state"]})

    respuesta_segunda_vez = client.get(
        "/api/sso/callback", params={"code": parametros_callback["code"], "state": parametros_callback["state"]}
    )
    assert respuesta_segunda_vez.status_code == 400


def test_state_desconocido_es_rechazado(client):
    respuesta = client.get("/api/sso/callback", params={"code": "cualquier-codigo", "state": "state-inventado"})
    assert respuesta.status_code == 400


def test_login_sso_con_el_mismo_correo_de_una_cuenta_existente_la_vincula_en_vez_de_duplicarla(client, test_engine):
    registrar(client, nombre="Carla Original", email="carla@externo.com")

    parametros = _extraer_query(client.get("/api/sso/iniciar").json()["url_autorizacion"])
    respuesta_autorizar = client.get(
        "/mock-idp/autorizar",
        params={
            "client_id": parametros["client_id"],
            "redirect_uri": parametros["redirect_uri"],
            "state": parametros["state"],
            "email_simulado": "carla@externo.com",
            "nombre_simulado": "Carla Externa",
        },
    )
    parametros_callback = _extraer_query(respuesta_autorizar.headers["location"])
    client.get("/api/sso/callback", params={"code": parametros_callback["code"], "state": parametros_callback["state"]})

    with test_engine.connect() as conexion:
        total_usuarios = conexion.exec_driver_sql("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        total_vinculos = conexion.exec_driver_sql("SELECT COUNT(*) FROM cuentas_externas").fetchone()[0]

    assert total_usuarios == 1
    assert total_vinculos == 1


def test_mock_idp_rechaza_client_secret_incorrecto_en_el_endpoint_de_token(client):
    parametros = _extraer_query(client.get("/api/sso/iniciar").json()["url_autorizacion"])
    respuesta_autorizar = client.get(
        "/mock-idp/autorizar",
        params={
            "client_id": parametros["client_id"],
            "redirect_uri": parametros["redirect_uri"],
            "state": parametros["state"],
            "email_simulado": "carla@externo.com",
            "nombre_simulado": "Carla Externa",
        },
    )
    parametros_callback = _extraer_query(respuesta_autorizar.headers["location"])

    respuesta_token = client.post(
        "/mock-idp/token",
        params={
            "grant_type": "authorization_code",
            "code": parametros_callback["code"],
            "redirect_uri": parametros["redirect_uri"],
            "client_id": parametros["client_id"],
            "client_secret": "secreto-incorrecto",
        },
    )
    assert respuesta_token.status_code == 400


def test_mock_idp_userinfo_requiere_un_access_token_valido(client):
    respuesta = client.get("/mock-idp/userinfo", headers={"Authorization": "Bearer token-invalido"})
    assert respuesta.status_code == 401
