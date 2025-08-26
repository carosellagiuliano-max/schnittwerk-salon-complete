from sqlalchemy.orm import Session
from . import models, auth
from .database import SessionLocal, engine

def init_database():
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        existing_admin = db.query(models.User).filter(models.User.is_admin == True).first()
        if not existing_admin:
            admin_user = models.User(
                email="admin@schnittwerk.com",
                hashed_password=auth.get_password_hash("admin123"),
                first_name="Admin",
                last_name="User",
                is_admin=True,
                is_active=True
            )
            db.add(admin_user)
        
        existing_services = db.query(models.Service).first()
        if not existing_services:
            services_data = [
                {
                    "name": "Damenschnitt kurz",
                    "description": "Professioneller Haarschnitt für kurze Haare",
                    "category": "women",
                    "service_type": "haircut",
                    "price_from": 65.0,
                    "duration_minutes": 60
                },
                {
                    "name": "Damenschnitt lang",
                    "description": "Professioneller Haarschnitt für lange Haare",
                    "category": "women", 
                    "service_type": "haircut",
                    "price_from": 85.0,
                    "duration_minutes": 90
                },
                {
                    "name": "Herrenschnitt",
                    "description": "Klassischer Herrenhaarschnitt",
                    "category": "men",
                    "service_type": "haircut", 
                    "price_from": 45.0,
                    "duration_minutes": 45
                },
                {
                    "name": "Waschen & Föhnen",
                    "description": "Haare waschen und föhnen",
                    "category": "both",
                    "service_type": "additional",
                    "price_from": 25.0,
                    "duration_minutes": 30
                },
                {
                    "name": "Färben",
                    "description": "Professionelle Haarfärbung",
                    "category": "both",
                    "service_type": "additional",
                    "price_from": 80.0,
                    "duration_minutes": 120
                }
            ]
            
            for service_data in services_data:
                service = models.Service(**service_data)
                db.add(service)
        
        existing_stylists = db.query(models.Stylist).first()
        if not existing_stylists:
            stylists_data = [
                {
                    "name": "Maria Schmidt",
                    "email": "maria@schnittwerk.com",
                    "phone": "+41 71 123 4567",
                    "specialties": "Damenschnitte, Färben"
                },
                {
                    "name": "Thomas Müller", 
                    "email": "thomas@schnittwerk.com",
                    "phone": "+41 71 123 4568",
                    "specialties": "Herrenschnitte, Bartpflege"
                }
            ]
            
            for stylist_data in stylists_data:
                stylist = models.Stylist(**stylist_data)
                db.add(stylist)
        
        existing_availability = db.query(models.StylistAvailability).first()
        if not existing_availability:
            for stylist_id in [1, 2]:
                for day in range(1, 6):
                    availability = models.StylistAvailability(
                        stylist_id=stylist_id,
                        day_of_week=day,
                        start_time="09:00",
                        end_time="18:00"
                    )
                    db.add(availability)
        
        db.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
