from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, appointments, admin, services

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Schnittwerk Salon API", version="1.0.0")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"])
app.include_router(services.router, prefix="/api/services", tags=["services"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Schnittwerk Salon API"}
