from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    appointments = relationship("Appointment", back_populates="customer")

class Stylist(Base):
    __tablename__ = "stylists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    specialties = Column(Text)  # JSON string of specialties
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    appointments = relationship("Appointment", back_populates="stylist")
    availability = relationship("StylistAvailability", back_populates="stylist")

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False)  # 'women', 'men'
    service_type = Column(String, nullable=False)  # 'haircut', 'additional'
    price_from = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stylist_id = Column(Integer, ForeignKey("stylists.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, default="confirmed")  # confirmed, cancelled, completed
    additional_services = Column(Text)  # JSON string of additional services
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("User", back_populates="appointments")
    stylist = relationship("Stylist", back_populates="appointments")
    service = relationship("Service")

class StylistAvailability(Base):
    __tablename__ = "stylist_availability"

    id = Column(Integer, primary_key=True, index=True)
    stylist_id = Column(Integer, ForeignKey("stylists.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(String, nullable=False)  # HH:MM format
    end_time = Column(String, nullable=False)  # HH:MM format
    is_active = Column(Boolean, default=True)

    stylist = relationship("Stylist", back_populates="availability")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    detailed_description = Column(Text)
    usage = Column(Text)
    price = Column(String, nullable=False)
    image = Column(String, nullable=False)
    category = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
