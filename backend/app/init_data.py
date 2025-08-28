from sqlalchemy.orm import Session
from . import models, auth
from .database import SessionLocal, engine
import os

def init_database():
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        existing_tenant = db.query(models.Tenant).filter(models.Tenant.id == "t_dev").first()
        if not existing_tenant:
            tenant = models.Tenant(
                id="t_dev",
                name="Schnittwerk Development",
                domain="localhost"
            )
            db.add(tenant)
        
        existing_admin = db.query(models.Profile).filter(
            models.Profile.tenant_id == "t_dev",
            models.Profile.role == "owner"
        ).first()
        if existing_admin:
            existing_admin.email = "admin@schnittwerk.com"
            existing_admin.hashed_password = auth.get_password_hash("admin123")
        else:
            admin_profile = models.Profile(
                tenant_id="t_dev",
                email="admin@schnittwerk.com",
                role="owner",
                full_name="Admin User",
                hashed_password=auth.get_password_hash("admin123")
            )
            db.add(admin_profile)
        
        existing_services = db.query(models.Service).filter(models.Service.tenant_id == "t_dev").first()
        if not existing_services:
            services_data = [
                {"name": "Damenschnitt", "duration_min": 60, "price_cents": 6500},
                {"name": "Herrenschnitt", "duration_min": 45, "price_cents": 4500},
                {"name": "Färben", "duration_min": 120, "price_cents": 8000},
            ]
            
            for service_data in services_data:
                service = models.Service(tenant_id="t_dev", **service_data)
                db.add(service)
        
        existing_staff = db.query(models.Staff).filter(models.Staff.tenant_id == "t_dev").first()
        if not existing_staff:
            staff_data = [
                {"name": "Maria Schmidt"},
                {"name": "Thomas Müller"},
            ]
            
            for staff_item in staff_data:
                staff = models.Staff(tenant_id="t_dev", **staff_item)
                db.add(staff)
        
        db.commit()
        print("Multi-tenant database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
