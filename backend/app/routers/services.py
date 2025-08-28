from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..middleware import get_tenant_id

router = APIRouter()

@router.get("/", response_model=List[schemas.Service])
async def get_services(
    request: Request,
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    services = db.query(models.Service).filter(
        models.Service.tenant_id == tenant_id,
        models.Service.active == True
    ).all()
    return services

@router.get("/{service_id}", response_model=schemas.Service)
async def get_service(service_id: int, request: Request, db: Session = Depends(get_db)):
    tenant_id = get_tenant_id(request)
    service = db.query(models.Service).filter(
        models.Service.tenant_id == tenant_id,
        models.Service.id == service_id
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
