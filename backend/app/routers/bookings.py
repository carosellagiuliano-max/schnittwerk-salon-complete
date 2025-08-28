from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_profile, get_current_admin
from ..middleware import get_tenant_id

router = APIRouter()

@router.post("/", response_model=schemas.Booking)
async def create_booking(
    request: Request,
    booking: schemas.BookingBase,
    current_profile: models.Profile = Depends(get_current_profile),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    ban = db.query(models.CustomerBan).filter(
        models.CustomerBan.tenant_id == tenant_id,
        models.CustomerBan.email == booking.customer_email
    ).first()
    if ban:
        raise HTTPException(status_code=403, detail="Customer is banned")
    
    service = db.query(models.Service).filter(
        models.Service.tenant_id == tenant_id,
        models.Service.id == booking.service_id,
        models.Service.active == True
    ).first()
    if not service: 
        raise HTTPException(status_code=404, detail="Service not found")
    
    end_at = booking.start_at + timedelta(minutes=service.duration_min)
    
    existing_booking = db.query(models.Booking).filter(
        models.Booking.tenant_id == tenant_id,
        models.Booking.staff_id == booking.staff_id,
        models.Booking.status == "CONFIRMED",
        models.Booking.start_at < end_at,
        models.Booking.end_at > booking.start_at
    ).first()
    
    if existing_booking:
        raise HTTPException(status_code=409, detail="Time slot conflict")
    
    db_booking = models.Booking(
        tenant_id=tenant_id,
        service_id=booking.service_id,
        staff_id=booking.staff_id,
        customer_email=booking.customer_email,
        start_at=booking.start_at,
        end_at=end_at,
        created_by=current_profile.email
    )
    
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@router.get("/me", response_model=List[schemas.Booking])
async def get_my_bookings(
    request: Request,
    current_profile: models.Profile = Depends(get_current_profile),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    bookings = db.query(models.Booking).filter(
        models.Booking.tenant_id == tenant_id,
        models.Booking.customer_email == current_profile.email
    ).all()
    return bookings

@router.delete("/{booking_id}")
async def cancel_booking(
    request: Request,
    booking_id: int,
    current_profile: models.Profile = Depends(get_current_profile),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    booking = db.query(models.Booking).filter(
        models.Booking.tenant_id == tenant_id,
        models.Booking.id == booking_id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if current_profile.role == "customer":
        if booking.customer_email != current_profile.email:
            raise HTTPException(status_code=403, detail="Not your booking")
        
        time_until = booking.start_at - datetime.utcnow()
        if time_until < timedelta(hours=24):
            raise HTTPException(status_code=400, detail="Cannot cancel less than 24h before")
    
    booking.status = "CANCELLED"
    booking.cancelled_by = current_profile.email
    db.commit()
    
    return {"message": "Booking cancelled successfully"}
