import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

from app.database import Base, get_db
from app.main import app
from app.models import Tenant, Profile, Service, Staff, Booking, CustomerBan
from app.auth import get_password_hash, create_access_token

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
    
    tenant = Tenant(id="t_test", name="Test Tenant", domain="test.example.com")
    db.add(tenant)
    
    admin = Profile(
        tenant_id="t_test",
        email="admin@test.com",
        role="admin",
        full_name="Admin User",
        hashed_password=get_password_hash("password")
    )
    customer = Profile(
        tenant_id="t_test",
        email="customer@test.com",
        role="customer",
        full_name="Customer User",
        hashed_password=get_password_hash("password")
    )
    banned_customer = Profile(
        tenant_id="t_test",
        email="banned@test.com",
        role="customer",
        full_name="Banned User",
        hashed_password=get_password_hash("password")
    )
    db.add(admin)
    db.add(customer)
    db.add(banned_customer)
    
    service = Service(
        tenant_id="t_test",
        name="Test Service",
        duration_min=60,
        price_cents=5000
    )
    staff = Staff(
        tenant_id="t_test",
        name="Test Staff",
        active=True
    )
    db.add(service)
    db.add(staff)
    
    ban = CustomerBan(
        tenant_id="t_test",
        email="banned@test.com",
        reason="Test ban"
    )
    db.add(ban)
    
    existing_booking = Booking(
        tenant_id="t_test",
        service_id=1,
        staff_id=1,
        customer_email="customer@test.com",
        start_at=datetime.utcnow() + timedelta(days=1, hours=10),
        end_at=datetime.utcnow() + timedelta(days=1, hours=11),
        status="CONFIRMED",
        created_by="customer@test.com"
    )
    db.add(existing_booking)
    
    db.commit()
    
    admin_token = create_access_token(
        data={"sub": "admin@test.com", "tenant_id": "t_test"},
        expires_delta=timedelta(minutes=30)
    )
    customer_token = create_access_token(
        data={"sub": "customer@test.com", "tenant_id": "t_test"},
        expires_delta=timedelta(minutes=30)
    )
    banned_token = create_access_token(
        data={"sub": "banned@test.com", "tenant_id": "t_test"},
        expires_delta=timedelta(minutes=30)
    )
    
    yield {
        "admin_token": admin_token,
        "customer_token": customer_token,
        "banned_token": banned_token,
        "existing_booking_id": existing_booking.id
    }
    
    db.query(Booking).delete()
    db.query(CustomerBan).delete()
    db.query(Staff).delete()
    db.query(Service).delete()
    db.query(Profile).delete()
    db.query(Tenant).delete()
    db.commit()
    db.close()

def test_banned_customer_booking(setup_test_data, monkeypatch):
    def mock_get_tenant_id(*args, **kwargs):
        return "t_test"
    
    monkeypatch.setattr("app.routers.bookings.get_tenant_id", mock_get_tenant_id)
    
    response = client.post(
        "/api/bookings/",
        headers={"Authorization": f"Bearer {setup_test_data['banned_token']}"},
        json={
            "service_id": 1,
            "staff_id": 1,
            "customer_email": "banned@test.com",
            "start_at": (datetime.utcnow() + timedelta(days=2)).isoformat()
        }
    )
    
    assert response.status_code == 403
    assert "banned" in response.json()["detail"].lower()

def test_booking_conflict(setup_test_data, monkeypatch):
    def mock_get_tenant_id(*args, **kwargs):
        return "t_test"
    
    monkeypatch.setattr("app.routers.bookings.get_tenant_id", mock_get_tenant_id)
    
    conflict_time = datetime.utcnow() + timedelta(days=1, hours=10, minutes=30)
    
    response = client.post(
        "/api/bookings/",
        headers={"Authorization": f"Bearer {setup_test_data['customer_token']}"},
        json={
            "service_id": 1,
            "staff_id": 1,
            "customer_email": "customer@test.com",
            "start_at": conflict_time.isoformat()
        }
    )
    
    assert response.status_code == 409
    assert "conflict" in response.json()["detail"].lower()

def test_customer_24h_cancellation(setup_test_data, monkeypatch):
    def mock_get_tenant_id(*args, **kwargs):
        return "t_test"
    
    monkeypatch.setattr("app.routers.bookings.get_tenant_id", mock_get_tenant_id)
    
    db = TestingSessionLocal()
    
    soon_booking = Booking(
        tenant_id="t_test",
        service_id=1,
        staff_id=1,
        customer_email="customer@test.com",
        start_at=datetime.utcnow() + timedelta(hours=12),
        end_at=datetime.utcnow() + timedelta(hours=13),
        status="CONFIRMED",
        created_by="customer@test.com"
    )
    db.add(soon_booking)
    db.commit()
    
    response = client.delete(
        f"/api/bookings/{soon_booking.id}",
        headers={"Authorization": f"Bearer {setup_test_data['customer_token']}"}
    )
    
    assert response.status_code == 400
    assert "24h" in response.json()["detail"].lower()
    
    response = client.delete(
        f"/api/admin/bookings/{soon_booking.id}",
        headers={"Authorization": f"Bearer {setup_test_data['admin_token']}"}
    )
    
    assert response.status_code == 200
    
    db.delete(soon_booking)
    db.commit()
    db.close()
