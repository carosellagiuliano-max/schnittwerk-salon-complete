from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_admin
from ..middleware import get_tenant_id

router = APIRouter()

@router.get("/services", response_model=List[schemas.Service])
async def get_all_services(
    request: Request,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    services = db.query(models.Service).filter(
        models.Service.tenant_id == tenant_id
    ).all()
    return services

@router.post("/services", response_model=schemas.Service)
async def create_service(
    request: Request,
    service: schemas.ServiceBase,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    existing = db.query(models.Service).filter(
        models.Service.tenant_id == tenant_id,
        models.Service.name == service.name
    ).first()
    if existing:
        raise HTTPException(status_code=422, detail="Service name already exists")
    
    if service.duration_min < 10:
        raise HTTPException(status_code=422, detail="Duration must be at least 10 minutes")
    if service.price_cents < 0:
        raise HTTPException(status_code=422, detail="Price must be non-negative")
    
    db_service = models.Service(
        tenant_id=tenant_id,
        **service.dict()
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.put("/services/{service_id}", response_model=schemas.Service)
async def update_service(
    request: Request,
    service_id: int,
    service: schemas.ServiceBase,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    db_service = db.query(models.Service).filter(
        models.Service.tenant_id == tenant_id,
        models.Service.id == service_id
    ).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if service.duration_min < 10:
        raise HTTPException(status_code=422, detail="Duration must be at least 10 minutes")
    if service.price_cents < 0:
        raise HTTPException(status_code=422, detail="Price must be non-negative")
    
    for key, value in service.dict().items():
        setattr(db_service, key, value)
    
    db.commit()
    db.refresh(db_service)
    return db_service

@router.delete("/services/{service_id}")
async def delete_service(
    request: Request,
    service_id: int,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    db_service = db.query(models.Service).filter(
        models.Service.tenant_id == tenant_id,
        models.Service.id == service_id
    ).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    db_service.active = False
    db.commit()
    return {"message": "Service deleted successfully"}

@router.get("/staff", response_model=List[schemas.Staff])
async def get_all_staff(
    request: Request,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    staff = db.query(models.Staff).filter(
        models.Staff.tenant_id == tenant_id
    ).all()
    return staff

@router.post("/staff", response_model=schemas.Staff)
async def create_staff(
    request: Request,
    staff: schemas.StaffBase,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    db_staff = models.Staff(
        tenant_id=tenant_id,
        **staff.dict()
    )
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    return db_staff

@router.put("/staff/{staff_id}", response_model=schemas.Staff)
async def update_staff(
    request: Request,
    staff_id: int,
    staff: schemas.StaffBase,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    db_staff = db.query(models.Staff).filter(
        models.Staff.tenant_id == tenant_id,
        models.Staff.id == staff_id
    ).first()
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    for key, value in staff.dict().items():
        setattr(db_staff, key, value)
    
    db.commit()
    db.refresh(db_staff)
    return db_staff

@router.delete("/staff/{staff_id}")
async def delete_staff(
    request: Request,
    staff_id: int,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    db_staff = db.query(models.Staff).filter(
        models.Staff.tenant_id == tenant_id,
        models.Staff.id == staff_id
    ).first()
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    db_staff.active = False
    db.commit()
    return {"message": "Staff deleted successfully"}

@router.get("/staff/{staff_id}/schedules", response_model=List[schemas.Schedule])
async def get_staff_schedules(
    request: Request,
    staff_id: int,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    staff = db.query(models.Staff).filter(
        models.Staff.tenant_id == tenant_id,
        models.Staff.id == staff_id
    ).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    schedules = db.query(models.Schedule).filter(
        models.Schedule.tenant_id == tenant_id,
        models.Schedule.staff_id == staff_id
    ).all()
    return schedules

@router.post("/staff/{staff_id}/schedules", response_model=schemas.Schedule)
async def create_staff_schedule(
    request: Request,
    staff_id: int,
    schedule: schemas.ScheduleBase,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    staff = db.query(models.Staff).filter(
        models.Staff.tenant_id == tenant_id,
        models.Staff.id == staff_id
    ).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    if schedule.start_min >= schedule.end_min:
        raise HTTPException(status_code=422, detail="Start time must be before end time")
    
    existing_schedule = db.query(models.Schedule).filter(
        models.Schedule.tenant_id == tenant_id,
        models.Schedule.staff_id == staff_id,
        models.Schedule.weekday == schedule.weekday,
        models.Schedule.start_min < schedule.end_min,
        models.Schedule.end_min > schedule.start_min
    ).first()
    
    if existing_schedule:
        raise HTTPException(status_code=409, detail="Schedule overlaps with existing schedule")
    
    db_schedule = models.Schedule(
        tenant_id=tenant_id,
        staff_id=staff_id,
        weekday=schedule.weekday,
        start_min=schedule.start_min,
        end_min=schedule.end_min
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@router.put("/staff/{staff_id}/schedules/{schedule_id}", response_model=schemas.Schedule)
async def update_staff_schedule(
    request: Request,
    staff_id: int,
    schedule_id: int,
    schedule: schemas.ScheduleBase,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    staff = db.query(models.Staff).filter(
        models.Staff.tenant_id == tenant_id,
        models.Staff.id == staff_id
    ).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    db_schedule = db.query(models.Schedule).filter(
        models.Schedule.tenant_id == tenant_id,
        models.Schedule.id == schedule_id,
        models.Schedule.staff_id == staff_id
    ).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    if schedule.start_min >= schedule.end_min:
        raise HTTPException(status_code=422, detail="Start time must be before end time")
    
    existing_schedule = db.query(models.Schedule).filter(
        models.Schedule.tenant_id == tenant_id,
        models.Schedule.staff_id == staff_id,
        models.Schedule.weekday == schedule.weekday,
        models.Schedule.start_min < schedule.end_min,
        models.Schedule.end_min > schedule.start_min,
        models.Schedule.id != schedule_id
    ).first()
    
    if existing_schedule:
        raise HTTPException(status_code=409, detail="Schedule overlaps with existing schedule")
    
    for key, value in schedule.dict().items():
        setattr(db_schedule, key, value)
    
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@router.delete("/staff/{staff_id}/schedules/{schedule_id}")
async def delete_staff_schedule(
    request: Request,
    staff_id: int,
    schedule_id: int,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    db_schedule = db.query(models.Schedule).filter(
        models.Schedule.tenant_id == tenant_id,
        models.Schedule.id == schedule_id,
        models.Schedule.staff_id == staff_id
    ).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(db_schedule)
    db.commit()
    return {"message": "Schedule deleted successfully"}

@router.get("/staff/{staff_id}/timeoff", response_model=List[schemas.TimeOff])
async def get_staff_timeoff(
    request: Request,
    staff_id: int,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    staff = db.query(models.Staff).filter(
        models.Staff.tenant_id == tenant_id,
        models.Staff.id == staff_id
    ).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    timeoffs = db.query(models.TimeOff).filter(
        models.TimeOff.tenant_id == tenant_id,
        models.TimeOff.staff_id == staff_id
    ).all()
    return timeoffs

@router.post("/staff/{staff_id}/timeoff", response_model=schemas.TimeOff)
async def create_staff_timeoff(
    request: Request,
    staff_id: int,
    timeoff: schemas.TimeOffBase,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    staff = db.query(models.Staff).filter(
        models.Staff.tenant_id == tenant_id,
        models.Staff.id == staff_id
    ).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    if timeoff.date_from > timeoff.date_to:
        raise HTTPException(status_code=422, detail="Start date must be before or equal to end date")
    
    db_timeoff = models.TimeOff(
        tenant_id=tenant_id,
        staff_id=staff_id,
        date_from=timeoff.date_from,
        date_to=timeoff.date_to,
        reason=timeoff.reason
    )
    db.add(db_timeoff)
    db.commit()
    db.refresh(db_timeoff)
    return db_timeoff

@router.put("/staff/{staff_id}/timeoff/{timeoff_id}", response_model=schemas.TimeOff)
async def update_staff_timeoff(
    request: Request,
    staff_id: int,
    timeoff_id: int,
    timeoff: schemas.TimeOffBase,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    staff = db.query(models.Staff).filter(
        models.Staff.tenant_id == tenant_id,
        models.Staff.id == staff_id
    ).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    db_timeoff = db.query(models.TimeOff).filter(
        models.TimeOff.tenant_id == tenant_id,
        models.TimeOff.id == timeoff_id,
        models.TimeOff.staff_id == staff_id
    ).first()
    if not db_timeoff:
        raise HTTPException(status_code=404, detail="TimeOff not found")
    
    if timeoff.date_from > timeoff.date_to:
        raise HTTPException(status_code=422, detail="Start date must be before or equal to end date")
    
    for key, value in timeoff.dict().items():
        setattr(db_timeoff, key, value)
    
    db.commit()
    db.refresh(db_timeoff)
    return db_timeoff

@router.delete("/staff/{staff_id}/timeoff/{timeoff_id}")
async def delete_staff_timeoff(
    request: Request,
    staff_id: int,
    timeoff_id: int,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    db_timeoff = db.query(models.TimeOff).filter(
        models.TimeOff.tenant_id == tenant_id,
        models.TimeOff.id == timeoff_id,
        models.TimeOff.staff_id == staff_id
    ).first()
    if not db_timeoff:
        raise HTTPException(status_code=404, detail="TimeOff not found")
    
    db.delete(db_timeoff)
    db.commit()
    return {"message": "TimeOff deleted successfully"}

@router.get("/bookings", response_model=List[schemas.Booking])
async def get_all_bookings(
    request: Request,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    bookings = db.query(models.Booking).filter(
        models.Booking.tenant_id == tenant_id
    ).all()
    return bookings

@router.delete("/bookings/{booking_id}")
async def admin_cancel_booking(
    request: Request,
    booking_id: int,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    booking = db.query(models.Booking).filter(
        models.Booking.tenant_id == tenant_id,
        models.Booking.id == booking_id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = "CANCELLED"
    booking.cancelled_by = current_admin.email
    db.commit()
    
    return {"message": "Booking cancelled successfully"}

@router.get("/customers", response_model=List[schemas.Profile])
async def get_all_customers(
    request: Request,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    customers = db.query(models.Profile).filter(
        models.Profile.tenant_id == tenant_id,
        models.Profile.role == "customer"
    ).all()
    return customers

@router.post("/customers/ban", response_model=schemas.CustomerBan)
async def ban_customer(
    request: Request,
    ban_data: schemas.CustomerBanBase,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    customer = db.query(models.Profile).filter(
        models.Profile.tenant_id == tenant_id,
        models.Profile.email == ban_data.email,
        models.Profile.role == "customer"
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    existing_ban = db.query(models.CustomerBan).filter(
        models.CustomerBan.tenant_id == tenant_id,
        models.CustomerBan.email == ban_data.email
    ).first()
    
    if existing_ban:
        raise HTTPException(status_code=400, detail="Customer already banned")
    
    db_ban = models.CustomerBan(
        tenant_id=tenant_id,
        email=ban_data.email,
        reason=ban_data.reason
    )
    db.add(db_ban)
    db.commit()
    db.refresh(db_ban)
    
    return db_ban

@router.delete("/customers/ban/{email}")
async def unban_customer(
    request: Request,
    email: str,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    ban = db.query(models.CustomerBan).filter(
        models.CustomerBan.tenant_id == tenant_id,
        models.CustomerBan.email == email
    ).first()
    
    if not ban:
        raise HTTPException(status_code=404, detail="Ban not found")
    
    db.delete(ban)
    db.commit()
    
    return {"message": "Customer unbanned successfully"}

@router.get("/tenant/settings", response_model=schemas.Tenant)
async def get_tenant_settings(
    request: Request,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    tenant = db.query(models.Tenant).filter(
        models.Tenant.id == tenant_id
    ).first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    return tenant

@router.put("/tenant/settings", response_model=schemas.Tenant)
async def update_tenant_settings(
    request: Request,
    settings: schemas.TenantBase,
    current_admin: models.Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    tenant = db.query(models.Tenant).filter(
        models.Tenant.id == tenant_id
    ).first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    settings_dict = settings.dict()
    if 'domain' in settings_dict:
        del settings_dict['domain']
    
    for key, value in settings_dict.items():
        setattr(tenant, key, value)
    
    db.commit()
    db.refresh(tenant)
    
    return tenant
