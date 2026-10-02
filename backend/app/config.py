import os


class Settings:
    database_url: str = os.getenv("BASTION_DATABASE_URL", "sqlite:///./bastion.db")
    jwt_secret: str = os.getenv("BASTION_JWT_SECRET", "bastion-clave-de-desarrollo-cambiar-en-produccion")
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 480
    login_temporal_expiration_minutes: int = 5
    emisor_totp: str = "Bastion"
    frontend_base_url: str = os.getenv("BASTION_FRONTEND_URL", "http://localhost:5176")
    backend_base_url: str = os.getenv("BASTION_BACKEND_URL", os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8030"))
    sso_client_id: str = "bastion-client"
    sso_client_secret: str = os.getenv("BASTION_SSO_CLIENT_SECRET", "bastion-sso-secret-de-desarrollo")


settings = Settings()
