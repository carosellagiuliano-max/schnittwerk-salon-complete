from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .middleware import TenantMiddleware
from .routers import auth, admin, services, availability, bookings
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Schnittwerk Multi-Tenant Salon API", version="2.0.0")

app.add_middleware(TenantMiddleware)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(services.router, prefix="/api/services", tags=["services"])
app.include_router(availability.router, prefix="/api", tags=["availability"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Schnittwerk Multi-Tenant Salon API v2.0"}
