from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List
from .. import models, schemas
from ..database import get_db
from ..middleware import get_tenant_id
import pytz

router = APIRouter()

@router.get("/availability")
async def get_availability(
    request: Request,
    service_id: int,
    staff_id: int,
    date: str,  # YYYY-MM-DD
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    service = db.query(models.Service).filter(
        models.Service.tenant_id == tenant_id,
        models.Service.id == service_id,
        models.Service.active == True
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    staff = db.query(models.Staff).filter(
        models.Staff.tenant_id == tenant_id,
        models.Staff.id == staff_id,
        models.Staff.active == True
    ).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    weekday = target_date.weekday()
    schedule = db.query(models.Schedule).filter(
        models.Schedule.tenant_id == tenant_id,
        models.Schedule.staff_id == staff_id,
        models.Schedule.weekday == weekday
    ).first()
    
    if not schedule:
        return []  # No schedule for this day
    
    time_off = db.query(models.TimeOff).filter(
        models.TimeOff.tenant_id == tenant_id,
        models.TimeOff.staff_id == staff_id,
        models.TimeOff.date_from <= target_date,
        models.TimeOff.date_to >= target_date
    ).first()
    
    if time_off:
        return []  # Staff is off this day
    
    tz = pytz.timezone("Europe/Zurich")
    start_time = datetime.combine(target_date, datetime.min.time()) + timedelta(minutes=schedule.start_min)
    end_time = datetime.combine(target_date, datetime.min.time()) + timedelta(minutes=schedule.end_min)
    
    start_utc = tz.localize(start_time).astimezone(pytz.UTC)
    end_utc = tz.localize(end_time).astimezone(pytz.UTC)
    
    existing_bookings = db.query(models.Booking).filter(
        models.Booking.tenant_id == tenant_id,
        models.Booking.staff_id == staff_id,
        models.Booking.start_at >= start_utc.replace(tzinfo=None),
        models.Booking.start_at < end_utc.replace(tzinfo=None),
        models.Booking.status == "CONFIRMED"
    ).all()
    
    available_slots = []
    current_time = start_utc
    
    while current_time + timedelta(minutes=service.duration_min) <= end_utc:
        slot_end = current_time + timedelta(minutes=service.duration_min)
        
        is_available = True
        for booking in existing_bookings:
            booking_start = booking.start_at.replace(tzinfo=pytz.UTC)
            booking_end = booking.end_at.replace(tzinfo=pytz.UTC)
            
            if (booking_start < slot_end and booking_end > current_time):
                is_available = False
                break
        
        if is_available:
            available_slots.append(current_time.isoformat())
        
        current_time += timedelta(minutes=service.duration_min)
    
    return available_slots
