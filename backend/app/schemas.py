from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_admin: bool
    is_active: bool
    is_blocked: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    service_type: str
    price_from: float
    duration_minutes: int

class Service(ServiceBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class StylistBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    specialties: Optional[str] = None

class Stylist(StylistBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    stylist_id: int
    service_id: int
    appointment_date: datetime
    additional_services: Optional[List[int]] = []
    notes: Optional[str] = None

class Appointment(BaseModel):
    id: int
    customer_id: int
    stylist_id: int
    service_id: int
    appointment_date: datetime
    duration_minutes: int
    total_price: float
    status: str
    additional_services: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    customer: User
    stylist: Stylist
    service: Service

    class Config:
        from_attributes = True

class AvailabilitySlot(BaseModel):
    date: str
    time: str
    stylist_id: int
    stylist_name: str
    available: bool
