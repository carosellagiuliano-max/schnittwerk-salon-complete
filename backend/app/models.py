from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, Float, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(String, primary_key=True)  # t_dev, t_salon1, etc.
    name = Column(String, nullable=False)
    domain = Column(String, unique=True, nullable=False)
    plan = Column(String, default="basic")
    theme_json = Column(Text)  # JSON string for theme config
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    profiles = relationship("Profile", back_populates="tenant")
    services = relationship("Service", back_populates="tenant")
    staff = relationship("Staff", back_populates="tenant")
    bookings = relationship("Booking", back_populates="tenant")

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'owner', 'admin', 'staff', 'customer'
    full_name = Column(String)
    phone = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant", back_populates="profiles")
    # Note: bookings relationship will be handled via queries, not SQLAlchemy relationship

class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    duration_min = Column(Integer, nullable=False)
    price_cents = Column(Integer, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant", back_populates="services")
    bookings = relationship("Booking", back_populates="service")

class Staff(Base):
    __tablename__ = "staff"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant", back_populates="staff")
    schedules = relationship("Schedule", back_populates="staff")
    time_offs = relationship("TimeOff", back_populates="staff")
    bookings = relationship("Booking", back_populates="staff")

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    weekday = Column(Integer, nullable=False)  # 0-6
    start_min = Column(Integer, nullable=False)  # minutes from midnight
    end_min = Column(Integer, nullable=False)
    
    staff = relationship("Staff", back_populates="schedules")

class TimeOff(Base):
    __tablename__ = "time_offs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    reason = Column(String)
    
    staff = relationship("Staff", back_populates="time_offs")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    customer_email = Column(String, nullable=False)
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="CONFIRMED")  # 'CONFIRMED', 'CANCELLED'
    created_by = Column(String)
    cancelled_by = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
    staff = relationship("Staff", back_populates="bookings")
    # Note: customer relationship will be handled via queries, not SQLAlchemy relationship

class CustomerBan(Base):
    __tablename__ = "customer_bans"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    email = Column(String, nullable=False)
    reason = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
