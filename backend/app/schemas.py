from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date

class TenantBase(BaseModel):
    name: str
    domain: str
    plan: Optional[str] = "basic"
    theme_json: Optional[str] = None

class Tenant(TenantBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProfileBase(BaseModel):
    email: EmailStr
    role: str  # 'owner', 'admin', 'staff', 'customer'
    full_name: Optional[str] = None
    phone: Optional[str] = None

class ProfileCreate(ProfileBase):
    password: str

class Profile(ProfileBase):
    id: int
    tenant_id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ServiceBase(BaseModel):
    name: str
    duration_min: int
    price_cents: int

class Service(ServiceBase):
    id: int
    tenant_id: str
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class StaffBase(BaseModel):
    name: str
    image_url: Optional[str] = None

class Staff(StaffBase):
    id: int
    tenant_id: str
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ScheduleBase(BaseModel):
    staff_id: int
    weekday: int
    start_min: int
    end_min: int

class Schedule(ScheduleBase):
    id: int
    tenant_id: str
    
    class Config:
        from_attributes = True

class TimeOffBase(BaseModel):
    staff_id: int
    date_from: date
    date_to: date
    reason: Optional[str] = None

class TimeOff(TimeOffBase):
    id: int
    tenant_id: str
    
    class Config:
        from_attributes = True

class BookingBase(BaseModel):
    service_id: int
    staff_id: int
    customer_email: str
    start_at: datetime

class Booking(BookingBase):
    id: int
    tenant_id: str
    end_at: datetime
    status: str
    created_by: Optional[str] = None
    cancelled_by: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class CustomerBanBase(BaseModel):
    email: EmailStr
    reason: Optional[str] = None

class CustomerBan(CustomerBanBase):
    id: int
    tenant_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginCredentials(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    profile: Profile
