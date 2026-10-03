# Bastion

Plataforma centralizada de autenticación y autorización para portafolio: 2FA con TOTP implementado a mano desde el RFC (no `pyotp`), RBAC completo, y un flujo real de SSO (OAuth2 Authorization Code) con un proveedor simulado para poder probarlo de punta a punta sin credenciales de Google.

## Arquitectura

```
┌──────────────────────┐
│  frontend              │
│  Vue 3 + TS (5176)     │
└──────────┬─────────────┘
           │ HTTP + JWT
┌──────────▼─────────────────────────────────────┐
│  backend (FastAPI, 8030)                          │
│  ├── auth: registro, login, login/2fa, refrescar   │
│  ├── 2fa: TOTP propio (RFC 6238)                   │
│  ├── rbac: roles, permisos, asignaciones           │
│  ├── sso: /api/sso/iniciar y /callback (cliente)   │
│  └── mock-idp: /autorizar /token /userinfo         │
│      (el proveedor SSO, simulado, vive aqui mismo) │
└─────────────────────────────────────────────────┘
```


## Requisitos

- Python 3.11+
- Node.js 18+

## Cómo levantarlo

### Backend — puerto 8030

```bash
cd backend
python3 -m venv venv
source venv/bin/activate      # en Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8030
```

### Frontend — puerto 5176

```bash
cd frontend
npm install
npm run dev
```

## Flujo para probarlo de punta a punta

1. Regístrate en `http://localhost:5176/registro` — el primer usuario que se registra se vuelve admin automáticamente (con permisos `admin:acceso`, `roles:administrar` y `usuarios:administrar`).
2. En "Mi cuenta", activa 2FA: escanea el QR con Google Authenticator (o cualquier app TOTP) o copia el secreto manual, y confirma con el código de 6 dígitos.
3. Cierra sesión y vuelve a entrar con tu correo y contraseña — ahora te va a pedir el código de la app antes de dejarte entrar.
4. Ve a "Administración": crea un rol nuevo, un permiso nuevo, asígnale el permiso al rol. Regístrate con una segunda cuenta en otra pestaña de incógnito y asígnale ese rol desde el admin.
5. Prueba el botón "Llamar a /api/demo/solo-admins" en "Mi cuenta" — solo funciona si tu usuario tiene el permiso `admin:acceso`.
6. Cierra sesión y en el login usa "Entrar con proveedor de prueba (SSO)" — te manda a una pantalla que simula el login de un proveedor externo (Google, por ejemplo), escribe cualquier correo/nombre, y vuelve a Bastion ya logueado con esa identidad.

## Las tres piezas, explicadas

### 2FA: TOTP implementado desde el RFC, no con una librería

`app/services/totp_service.py` implementa HOTP (RFC 4226) y TOTP (RFC 6238) usando solo `hmac` y `hashlib` de la librería estándar de Python — nada de `pyotp`. Está verificado contra los 6 vectores de prueba oficiales del Apéndice B del RFC 6238 (`tests/test_totp.py`), así que no es "debería funcionar", es "coincide byte por byte con lo que publicó el IETF".

### RBAC: permisos embebidos en el JWT

Un usuario tiene roles, un rol tiene permisos. Al hacer login, Bastion calcula el conjunto de permisos efectivos del usuario y los mete directo en el JWT, así que verificar un permiso en cualquier endpoint (`Depends(requerir_permiso("admin:acceso"))`) no cuesta una consulta extra a la base de datos.

El costo de esa decisión: si le cambias el rol a alguien, su JWT viejo sigue teniendo los permisos de antes hasta que expire o vuelva a loguearse. Por eso existe `POST /api/auth/refrescar` — reemite el token con los permisos actuales sin pedir contraseña de nuevo.

### SSO: el flujo real de OAuth2, con un proveedor de mentira

`/mock-idp/*` es un proveedor de identidad simulado (hace lo que haría `accounts.google.com`) que vive en el mismo backend, solo para poder probar el flujo completo sin necesitar credenciales reales de Google o Microsoft. Pero el protocolo que corre encima es el de verdad:

1. Bastion genera un `state` aleatorio (protección CSRF) y manda al usuario a la pantalla del proveedor.
2. El proveedor "autentica" al usuario y redirige de vuelta con un `code` de un solo uso.
3. Bastion valida el `state`, intercambia el `code` por un `access_token`, y con ese token pide los datos del usuario (`/userinfo`).
4. Busca o crea el usuario local por correo, vincula la cuenta externa, y emite su propio JWT de sesión.

Para no depender de una llamada HTTP real de Bastion hacia sí mismo (frágil de probar), el intercambio código→token y la consulta de userinfo se hacen como llamadas de función directas en vez de HTTP saliente — pero es exactamente la misma lógica que usarían esas llamadas HTTP contra un proveedor real, y los endpoints `/mock-idp/token` y `/mock-idp/userinfo` existen también como HTTP real por si quieres probarlos sueltos (hay pruebas que sí les pegan por HTTP).

## Pruebas automatizadas

33 pruebas con pytest, corridas y verificadas durante el desarrollo:

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

Cobertura: los 6 vectores oficiales del RFC 6238 para TOTP, tolerancia de reloj, registro/login, el flujo completo de activación y login con 2FA (incluyendo que un login temporal no se puede reusar dos veces), RBAC (quién puede crear roles, asignar permisos, que revocar un rol de verdad quita el permiso tras refrescar), y el flujo SSO completo de principio a fin (incluyendo que el `state` no se puede reutilizar y que loguearte por SSO con el correo de una cuenta existente la vincula en vez de duplicarla).

Pruebas de test
 33 pruebas pasaron sin encontrar ningún bug en el camino — el diseño se validó contra los vectores del RFC antes de construir el resto encima, lo cual probablemente ayudó.

## Despliegue (Vercel para el frontend, Render para el backend)