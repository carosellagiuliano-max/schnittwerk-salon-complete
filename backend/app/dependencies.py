from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .auth import verify_token
from .middleware import get_tenant_id
from . import models

security = HTTPBearer()

def get_current_profile(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    tenant_id = get_tenant_id(request)
    token = credentials.credentials
    email, token_tenant_id = verify_token(token)
    
    if email is None or token_tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    profile = db.query(models.Profile).filter(
        models.Profile.tenant_id == tenant_id,
        models.Profile.email == email
    ).first()
    
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Profile not found"
        )
    
    if not profile.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profile account is inactive"
        )
    
    return profile

def require_role(allowed_roles: list):
    def role_checker(current_profile: models.Profile = Depends(get_current_profile)):
        if current_profile.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_profile
    return role_checker

def get_current_admin(current_profile: models.Profile = Depends(require_role(['owner', 'admin']))):
    return current_profile

def get_current_customer(current_profile: models.Profile = Depends(require_role(['customer']))):
    return current_profile
