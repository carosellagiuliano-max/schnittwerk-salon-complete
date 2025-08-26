from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta, time
from typing import List
from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter()

@router.get("/availability")
async def get_availability(
    date: str,
    service_id: int,
    db: Session = Depends(get_db)
):
    try:
        appointment_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    stylists = db.query(models.Stylist).filter(models.Stylist.is_active == True).all()
    availability_slots = []
    
    for stylist in stylists:
        day_of_week = appointment_date.weekday()
        stylist_availability = db.query(models.StylistAvailability).filter(
            and_(
                models.StylistAvailability.stylist_id == stylist.id,
                models.StylistAvailability.day_of_week == day_of_week,
                models.StylistAvailability.is_active == True
            )
        ).first()
        
        if not stylist_availability:
            continue
        
        start_time = datetime.strptime(stylist_availability.start_time, "%H:%M").time()
        end_time = datetime.strptime(stylist_availability.end_time, "%H:%M").time()
        
        current_time = datetime.combine(appointment_date, start_time)
        end_datetime = datetime.combine(appointment_date, end_time)
        
        while current_time + timedelta(minutes=service.duration_minutes) <= end_datetime:
            appointment_datetime = current_time
            
            existing_appointments = db.query(models.Appointment).filter(
                and_(
                    models.Appointment.stylist_id == stylist.id,
                    models.Appointment.status == "confirmed"
                )
            ).all()
            
            existing_appointment = None
            for apt in existing_appointments:
                apt_start = apt.appointment_date
                apt_end = apt_start + timedelta(minutes=apt.duration_minutes)
                slot_start = appointment_datetime
                slot_end = slot_start + timedelta(minutes=service.duration_minutes)
                
                if apt_start < slot_end and apt_end > slot_start:
                    existing_appointment = apt
                    break
            
            is_available = existing_appointment is None
            
            availability_slots.append({
                "date": date,
                "time": current_time.strftime("%H:%M"),
                "stylist_id": stylist.id,
                "stylist_name": stylist.name,
                "available": is_available
            })
            
            current_time += timedelta(minutes=30)
    
    return availability_slots

@router.post("/", response_model=schemas.Appointment)
async def create_appointment(
    appointment: schemas.AppointmentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = db.query(models.Service).filter(models.Service.id == appointment.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    stylist = db.query(models.Stylist).filter(models.Stylist.id == appointment.stylist_id).first()
    if not stylist:
        raise HTTPException(status_code=404, detail="Stylist not found")
    
    existing_appointments = db.query(models.Appointment).filter(
        and_(
            models.Appointment.stylist_id == appointment.stylist_id,
            models.Appointment.status == "confirmed"
        )
    ).all()
    
    existing_appointment = None
    for apt in existing_appointments:
        apt_start = apt.appointment_date
        apt_end = apt_start + timedelta(minutes=apt.duration_minutes)
        slot_start = appointment.appointment_date
        slot_end = slot_start + timedelta(minutes=service.duration_minutes)
        
        if apt_start < slot_end and apt_end > slot_start:
            existing_appointment = apt
            break
    
    if existing_appointment:
        raise HTTPException(status_code=400, detail="Time slot not available")
    
    total_price = service.price_from
    additional_services_data = []
    
    if appointment.additional_services:
        for service_id in appointment.additional_services:
            add_service = db.query(models.Service).filter(models.Service.id == service_id).first()
            if add_service:
                total_price += add_service.price_from
                additional_services_data.append({
                    "id": add_service.id,
                    "name": add_service.name,
                    "price": add_service.price_from
                })
    
    db_appointment = models.Appointment(
        customer_id=current_user.id,
        stylist_id=appointment.stylist_id,
        service_id=appointment.service_id,
        appointment_date=appointment.appointment_date,
        duration_minutes=service.duration_minutes,
        total_price=total_price,
        additional_services=str(additional_services_data) if additional_services_data else None,
        notes=appointment.notes
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment

@router.get("/my-appointments", response_model=List[schemas.Appointment])
async def get_my_appointments(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointments = db.query(models.Appointment).filter(
        models.Appointment.customer_id == current_user.id
    ).all()
    return appointments

@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(models.Appointment).filter(
        and_(
            models.Appointment.id == appointment_id,
            models.Appointment.customer_id == current_user.id
        )
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment.status == "cancelled":
        raise HTTPException(status_code=400, detail="Appointment already cancelled")
    
    time_until_appointment = appointment.appointment_date - datetime.now()
    if time_until_appointment < timedelta(hours=24):
        raise HTTPException(
            status_code=400, 
            detail="Cannot cancel appointment less than 24 hours before scheduled time"
        )
    
    appointment.status = "cancelled"
    db.commit()
    
    return {"message": "Appointment cancelled successfully"}
