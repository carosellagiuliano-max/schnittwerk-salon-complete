import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta, date

from app.database import Base, get_db
from app.main import app
from app.models import Tenant, Service, Staff, Schedule, TimeOff, Booking

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
    
    service = Service(
        tenant_id="t_test",
        name="Test Service",
        duration_min=60,
        price_cents=5000,
        active=True
    )
    db.add(service)
    
    staff = Staff(
        tenant_id="t_test",
        name="Test Staff",
        active=True
    )
    db.add(staff)
    
    schedule = Schedule(
        tenant_id="t_test",
        staff_id=1,
        weekday=0,  # Monday
        start_min=540,  # 9:00 AM (9 * 60)
        end_min=1020  # 5:00 PM (17 * 60)
    )
    db.add(schedule)
    
    db.commit()
    
    today = date.today()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    
    yield {
        "service_id": service.id,
        "staff_id": staff.id,
        "next_monday": next_monday
    }
    
    db.query(Schedule).delete()
    db.query(Staff).delete()
    db.query(Service).delete()
    db.query(Tenant).delete()
    db.commit()
    db.close()

def test_availability_with_no_bookings(setup_test_data, monkeypatch):
    def mock_get_tenant_id(*args, **kwargs):
        return "t_test"
    
    monkeypatch.setattr("app.routers.availability.get_tenant_id", mock_get_tenant_id)
    
    next_monday = setup_test_data["next_monday"]
    
    response = client.get(
        f"/api/availability?service_id={setup_test_data['service_id']}&staff_id={setup_test_data['staff_id']}&date={next_monday.isoformat()}"
    )
    
    assert response.status_code == 200
    slots = response.json()
    
    assert len(slots) > 0
    
    first_slot = datetime.fromisoformat(slots[0].replace('Z', '+00:00'))
    last_slot = datetime.fromisoformat(slots[-1].replace('Z', '+00:00'))
    
    assert first_slot.hour >= 9  # May be later due to timezone conversion
    assert last_slot.hour < 17  # Last slot should start before 17:00

def test_availability_with_booking(setup_test_data, monkeypatch):
    def mock_get_tenant_id(*args, **kwargs):
        return "t_test"
    
    monkeypatch.setattr("app.routers.availability.get_tenant_id", mock_get_tenant_id)
    
    db = TestingSessionLocal()
    next_monday = setup_test_data["next_monday"]
    booking_start = datetime.combine(next_monday, datetime.min.time()) + timedelta(hours=11)
    booking_end = booking_start + timedelta(hours=1)
    
    booking = Booking(
        tenant_id="t_test",
        service_id=setup_test_data["service_id"],
        staff_id=setup_test_data["staff_id"],
        customer_email="test@example.com",
        start_at=booking_start,
        end_at=booking_end,
        status="CONFIRMED",
        created_by="test@example.com"
    )
    db.add(booking)
    db.commit()
    
    response = client.get(
        f"/api/availability?service_id={setup_test_data['service_id']}&staff_id={setup_test_data['staff_id']}&date={next_monday.isoformat()}"
    )
    
    assert response.status_code == 200
    slots = response.json()
    
    for slot in slots:
        slot_time = datetime.fromisoformat(slot.replace('Z', '+00:00'))
        assert slot_time.hour != 11 or slot_time.minute != 0
    
    db.delete(booking)
    db.commit()
    db.close()

def test_availability_with_time_off(setup_test_data, monkeypatch):
    def mock_get_tenant_id(*args, **kwargs):
        return "t_test"
    
    monkeypatch.setattr("app.routers.availability.get_tenant_id", mock_get_tenant_id)
    
    db = TestingSessionLocal()
    next_monday = setup_test_data["next_monday"]
    
    time_off = TimeOff(
        tenant_id="t_test",
        staff_id=setup_test_data["staff_id"],
        date_from=next_monday,
        date_to=next_monday,
        reason="Day off"
    )
    db.add(time_off)
    db.commit()
    
    response = client.get(
        f"/api/availability?service_id={setup_test_data['service_id']}&staff_id={setup_test_data['staff_id']}&date={next_monday.isoformat()}"
    )
    
    assert response.status_code == 200
    slots = response.json()
    
    assert len(slots) == 0
    
    db.delete(time_off)
    db.commit()
    db.close()
