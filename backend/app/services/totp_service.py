import base64
import hashlib
import hmac
import secrets
import time
from urllib.parse import quote

PASO_SEGUNDOS = 30
DIGITOS_POR_DEFECTO = 6
VENTANA_TOLERANCIA_PASOS = 1  # acepta +-1 paso (30s) para compensar desfases de reloj


def generar_secreto(longitud_bytes: int = 20) -> str:
    # base32 porque es el formato que leen Google Authenticator, Authy, etc.
    bytes_aleatorios = secrets.token_bytes(longitud_bytes)
    return base64.b32encode(bytes_aleatorios).decode("utf-8")


def _hotp_binario(secreto_bytes: bytes, contador: int, algoritmo=hashlib.sha1) -> int:
    # HOTP de RFC 4226: HMAC del contador, y luego "truncamiento dinamico"
    # (el ultimo nibble del hash dice de donde sacar los 4 bytes del codigo)
    contador_bytes = contador.to_bytes(8, byteorder="big")
    hash_hmac = hmac.new(secreto_bytes, contador_bytes, algoritmo).digest()

    offset = hash_hmac[-1] & 0x0F
    fragmento = hash_hmac[offset : offset + 4]
    codigo_binario = int.from_bytes(fragmento, byteorder="big") & 0x7FFFFFFF

    return codigo_binario


def hotp(secreto_bytes: bytes, contador: int, digitos: int = DIGITOS_POR_DEFECTO) -> str:
    codigo_binario = _hotp_binario(secreto_bytes, contador)
    codigo = codigo_binario % (10**digitos)
    return str(codigo).zfill(digitos)


def totp(
    secreto_base32: str,
    tiempo_unix: float | None = None,
    paso: int = PASO_SEGUNDOS,
    digitos: int = DIGITOS_POR_DEFECTO,
) -> str:
    if tiempo_unix is None:
        tiempo_unix = time.time()

    secreto_bytes = base64.b32decode(secreto_base32.upper())
    contador = int(tiempo_unix // paso)
    return hotp(secreto_bytes, contador, digitos)


def verificar_codigo(
    secreto_base32: str,
    codigo: str,
    tiempo_unix: float | None = None,
    ventana: int = VENTANA_TOLERANCIA_PASOS,
) -> bool:
    if tiempo_unix is None:
        tiempo_unix = time.time()

    codigo = codigo.strip()
    if not codigo.isdigit():
        return False

    for desplazamiento in range(-ventana, ventana + 1):
        candidato = totp(secreto_base32, tiempo_unix + desplazamiento * PASO_SEGUNDOS)
        if hmac.compare_digest(candidato, codigo):
            return True

    return False


def generar_uri_otpauth(secreto_base32: str, email_usuario: str, emisor: str) -> str:
    # este es el formato que lee la app autenticadora cuando escaneas el QR
    etiqueta = quote(f"{emisor}:{email_usuario}")
    emisor_codificado = quote(emisor)
    return f"otpauth://totp/{etiqueta}?secret={secreto_base32}&issuer={emisor_codificado}&algorithm=SHA1&digits={DIGITOS_POR_DEFECTO}&period={PASO_SEGUNDOS}"
