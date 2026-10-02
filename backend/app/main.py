from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models  # noqa: F401 - registra los modelos en el metadata
from app.routers import auth, demo, mock_idp, rbac, sso, twofa

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bastion",
    description="Plataforma centralizada de autenticacion y autorizacion: 2FA (TOTP propio), RBAC y SSO (OAuth2)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(twofa.router)
app.include_router(rbac.router)
app.include_router(demo.router)
app.include_router(sso.router)
app.include_router(mock_idp.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "bastion"}
