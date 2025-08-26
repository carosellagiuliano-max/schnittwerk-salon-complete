from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Service])
async def get_services(
    category: str = None,
    service_type: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Service).filter(models.Service.is_active == True)
    
    if category:
        query = query.filter(models.Service.category == category)
    if service_type:
        query = query.filter(models.Service.service_type == service_type)
    
    return query.all()

@router.get("/{service_id}", response_model=schemas.Service)
async def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
