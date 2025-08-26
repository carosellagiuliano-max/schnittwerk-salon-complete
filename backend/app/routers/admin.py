from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_admin_user

router = APIRouter()

@router.get("/appointments", response_model=List[schemas.Appointment])
async def get_all_appointments(
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    appointments = db.query(models.Appointment).all()
    return appointments

@router.delete("/appointments/{appointment_id}")
async def cancel_appointment_admin(
    appointment_id: int,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment.status = "cancelled"
    db.commit()
    
    return {"message": "Appointment cancelled by admin"}

@router.get("/customers", response_model=List[schemas.User])
async def get_all_customers(
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    customers = db.query(models.User).filter(models.User.is_admin == False).all()
    return customers

@router.put("/customers/{customer_id}/block")
async def block_customer(
    customer_id: int,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    customer = db.query(models.User).filter(models.User.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer.is_blocked = True
    db.commit()
    
    return {"message": "Customer blocked successfully"}

@router.put("/customers/{customer_id}/unblock")
async def unblock_customer(
    customer_id: int,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    customer = db.query(models.User).filter(models.User.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer.is_blocked = False
    db.commit()
    
    return {"message": "Customer unblocked successfully"}

@router.post("/services", response_model=schemas.Service)
async def create_service(
    service: schemas.ServiceBase,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_service = models.Service(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.put("/services/{service_id}", response_model=schemas.Service)
async def update_service(
    service_id: int,
    service: schemas.ServiceBase,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    for key, value in service.dict().items():
        setattr(db_service, key, value)
    
    db.commit()
    db.refresh(db_service)
    return db_service

@router.delete("/services/{service_id}")
async def delete_service(
    service_id: int,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    db_service.is_active = False
    db.commit()
    
    return {"message": "Service deleted successfully"}
