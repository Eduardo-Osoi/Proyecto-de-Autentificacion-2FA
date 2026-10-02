import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture()
def client(test_engine):
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, follow_redirects=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def registrar(client, nombre="Ana Admin", email="ana@bastion.com", password="clave12345") -> dict:
    respuesta = client.post("/api/auth/registro", json={"nombre": nombre, "email": email, "password": password})
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def encabezado_auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
