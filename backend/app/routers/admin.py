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

@router.get("/products", response_model=List[schemas.Product])
async def get_all_products(
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    products = db.query(models.Product).all()
    return products

@router.post("/products", response_model=schemas.Product)
async def create_product(
    product: schemas.ProductBase,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/products/{product_id}", response_model=schemas.Product)
async def update_product(
    product_id: int,
    product: schemas.ProductBase,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_product.is_active = False
    db.commit()
    
    return {"message": "Product deleted successfully"}

@router.get("/product-categories", response_model=List[schemas.ProductCategory])
async def get_product_categories(
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    categories = db.query(models.ProductCategory).all()
    return categories

@router.post("/product-categories", response_model=schemas.ProductCategory)
async def create_product_category(
    category: schemas.ProductCategoryBase,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_category = models.ProductCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/stylists", response_model=List[schemas.Stylist])
async def get_all_stylists(
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    stylists = db.query(models.Stylist).all()
    return stylists

@router.post("/stylists", response_model=schemas.Stylist)
async def create_stylist(
    stylist: schemas.StylistBase,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_stylist = models.Stylist(**stylist.dict())
    db.add(db_stylist)
    db.commit()
    db.refresh(db_stylist)
    return db_stylist

@router.put("/stylists/{stylist_id}", response_model=schemas.Stylist)
async def update_stylist(
    stylist_id: int,
    stylist: schemas.StylistBase,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_stylist = db.query(models.Stylist).filter(models.Stylist.id == stylist_id).first()
    if not db_stylist:
        raise HTTPException(status_code=404, detail="Stylist not found")
    
    for key, value in stylist.dict().items():
        setattr(db_stylist, key, value)
    
    db.commit()
    db.refresh(db_stylist)
    return db_stylist

@router.delete("/stylists/{stylist_id}")
async def delete_stylist(
    stylist_id: int,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_stylist = db.query(models.Stylist).filter(models.Stylist.id == stylist_id).first()
    if not db_stylist:
        raise HTTPException(status_code=404, detail="Stylist not found")
    
    db_stylist.is_active = False
    db.commit()
    
    return {"message": "Stylist deleted successfully"}

@router.get("/stylist-availability/{stylist_id}", response_model=List[schemas.StylistAvailability])
async def get_stylist_availability(
    stylist_id: int,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    availability = db.query(models.StylistAvailability).filter(
        models.StylistAvailability.stylist_id == stylist_id
    ).all()
    return availability

@router.post("/stylist-availability", response_model=schemas.StylistAvailability)
async def create_stylist_availability(
    availability: schemas.StylistAvailabilityBase,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_availability = models.StylistAvailability(**availability.dict())
    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)
    return db_availability

@router.put("/stylist-availability/{availability_id}", response_model=schemas.StylistAvailability)
async def update_stylist_availability(
    availability_id: int,
    availability: schemas.StylistAvailabilityBase,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_availability = db.query(models.StylistAvailability).filter(
        models.StylistAvailability.id == availability_id
    ).first()
    if not db_availability:
        raise HTTPException(status_code=404, detail="Availability not found")
    
    for key, value in availability.dict().items():
        setattr(db_availability, key, value)
    
    db.commit()
    db.refresh(db_availability)
    return db_availability

@router.delete("/stylist-availability/{availability_id}")
async def delete_stylist_availability(
    availability_id: int,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_availability = db.query(models.StylistAvailability).filter(
        models.StylistAvailability.id == availability_id
    ).first()
    if not db_availability:
        raise HTTPException(status_code=404, detail="Availability not found")
    
    db_availability.is_active = False
    db.commit()
    
    return {"message": "Availability deleted successfully"}
