from app.database import SessionLocal, engine
from app.models import Base
from app.init_data import init_database

def create_tables_and_init():
    Base.metadata.create_all(bind=engine)
    print("Database tables created")
    
    init_database()
    print("Database initialized with sample data")

if __name__ == "__main__":
    create_tables_and_init()
