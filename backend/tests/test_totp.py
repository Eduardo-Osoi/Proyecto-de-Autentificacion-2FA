from app.services.totp_service import (
    generar_secreto,
    generar_uri_otpauth,
    hotp,
    totp,
    verificar_codigo,
)

SECRETO_RFC_ASCII = b"12345678901234567890"

VECTORES_RFC_6238 = [
    (59, "94287082"),
    (1111111109, "07081804"),
    (1111111111, "14050471"),
    (1234567890, "89005924"),
    (2000000000, "69279037"),
    (20000000000, "65353130"),
]


def test_hotp_coincide_con_los_vectores_oficiales_del_rfc_6238():
    for tiempo, esperado in VECTORES_RFC_6238:
        contador = tiempo // 30
        assert hotp(SECRETO_RFC_ASCII, contador, digitos=8) == esperado


def test_totp_genera_codigos_de_seis_digitos_por_defecto():
    secreto = generar_secreto()
    codigo = totp(secreto)
    assert len(codigo) == 6
    assert codigo.isdigit()


def test_verificar_codigo_acepta_el_codigo_correcto_del_momento_actual():
    secreto = generar_secreto()
    codigo_actual = totp(secreto)
    assert verificar_codigo(secreto, codigo_actual) is True


def test_verificar_codigo_rechaza_un_codigo_incorrecto():
    secreto = generar_secreto()
    assert verificar_codigo(secreto, "000000") is False


def test_verificar_codigo_tolera_un_paso_de_desfase_de_reloj():
    secreto = generar_secreto()
    tiempo_base = 1_700_000_000
    codigo_paso_anterior = totp(secreto, tiempo_unix=tiempo_base - 30)
    assert verificar_codigo(secreto, codigo_paso_anterior, tiempo_unix=tiempo_base) is True


def test_verificar_codigo_rechaza_un_codigo_fuera_de_la_ventana_de_tolerancia():
    secreto = generar_secreto()
    tiempo_base = 1_700_000_000
    codigo_lejano = totp(secreto, tiempo_unix=tiempo_base - 300)
    assert verificar_codigo(secreto, codigo_lejano, tiempo_unix=tiempo_base) is False


def test_verificar_codigo_rechaza_entrada_no_numerica():
    secreto = generar_secreto()
    assert verificar_codigo(secreto, "abcdef") is False


def test_dos_secretos_generados_son_distintos():
    assert generar_secreto() != generar_secreto()


def test_uri_otpauth_contiene_los_campos_esperados():
    uri = generar_uri_otpauth("JBSWY3DPEHPK3PXP", "ana@bastion.com", "Bastion")
    assert uri.startswith("otpauth://totp/")
    assert "secret=JBSWY3DPEHPK3PXP" in uri
    assert "issuer=Bastion" in uri
