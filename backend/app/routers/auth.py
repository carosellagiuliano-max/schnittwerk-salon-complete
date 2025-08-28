from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import models, schemas, auth
from ..dependencies import get_current_profile
from ..database import get_db
from ..middleware import get_tenant_id

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    request: Request,
    credentials: schemas.LoginCredentials,
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    profile = auth.authenticate_profile(db, tenant_id, credentials.email, credentials.password)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not profile.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": profile.email, "tenant_id": tenant_id}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "profile": profile}

@router.post("/register", response_model=schemas.Profile)
async def register_customer(
    request: Request,
    profile_data: schemas.ProfileCreate,
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    
    existing_profile = auth.get_profile(db, tenant_id, profile_data.email)
    if existing_profile:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    profile_data.role = "customer"
    
    hashed_password = auth.get_password_hash(profile_data.password)
    db_profile = models.Profile(
        tenant_id=tenant_id,
        email=profile_data.email,
        role="customer",
        full_name=profile_data.full_name,
        phone=profile_data.phone,
        hashed_password=hashed_password
    )
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile

@router.get("/me", response_model=schemas.Profile)
async def read_profile_me(
    current_profile: models.Profile = Depends(get_current_profile),
):
    return current_profile
