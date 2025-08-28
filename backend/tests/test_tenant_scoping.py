import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Tenant, Profile, Service
from app.auth import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def setup_test_data():
    db = TestingSessionLocal()
    
    tenant1 = Tenant(id="t_test1", name="Test Tenant 1", domain="test1.example.com")
    tenant2 = Tenant(id="t_test2", name="Test Tenant 2", domain="test2.example.com")
    db.add(tenant1)
    db.add(tenant2)
    
    admin1 = Profile(
        tenant_id="t_test1",
        email="admin1@test.com",
        role="admin",
        full_name="Admin One",
        hashed_password=get_password_hash("password1")
    )
    admin2 = Profile(
        tenant_id="t_test2",
        email="admin2@test.com",
        role="admin",
        full_name="Admin Two",
        hashed_password=get_password_hash("password2")
    )
    db.add(admin1)
    db.add(admin2)
    
    service1 = Service(
        tenant_id="t_test1",
        name="Service 1",
        duration_min=60,
        price_cents=5000
    )
    service2 = Service(
        tenant_id="t_test2",
        name="Service 2",
        duration_min=45,
        price_cents=3500
    )
    db.add(service1)
    db.add(service2)
    
    db.commit()
    
    yield
    
    db.query(Service).delete()
    db.query(Profile).delete()
    db.query(Tenant).delete()
    db.commit()
    db.close()

def test_tenant_scoping(setup_test_data, monkeypatch):
    def mock_get_tenant_id_1(*args, **kwargs):
        return "t_test1"
    
    def mock_get_tenant_id_2(*args, **kwargs):
        return "t_test2"
    
    from app.middleware import get_tenant_id
    monkeypatch.setattr("app.routers.auth.get_tenant_id", mock_get_tenant_id_1)
    
    response = client.post(
        "/api/auth/login",
        json={"email": "admin1@test.com", "password": "password1"}
    )
    assert response.status_code == 200
    token1 = response.json()["access_token"]
    
    monkeypatch.setattr("app.routers.auth.get_tenant_id", mock_get_tenant_id_2)
    
    response = client.post(
        "/api/auth/login",
        json={"email": "admin2@test.com", "password": "password2"}
    )
    assert response.status_code == 200
    token2 = response.json()["access_token"]
    
    monkeypatch.setattr("app.routers.services.get_tenant_id", mock_get_tenant_id_1)
    
    response = client.get("/api/services")
    assert response.status_code == 200
    services = response.json()
    assert len(services) == 1
    assert services[0]["name"] == "Service 1"
    
    monkeypatch.setattr("app.routers.services.get_tenant_id", mock_get_tenant_id_2)
    
    response = client.get("/api/services")
    assert response.status_code == 200
    services = response.json()
    assert len(services) == 1
    assert services[0]["name"] == "Service 2"
    
    monkeypatch.setattr("app.routers.admin.get_tenant_id", mock_get_tenant_id_2)
    monkeypatch.setattr("app.dependencies.get_tenant_id", mock_get_tenant_id_2)
    
    response = client.get(
        "/api/admin/services",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert response.status_code == 401  # Should fail with unauthorized
