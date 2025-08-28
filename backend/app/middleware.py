from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import os

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if os.getenv("DEV_MODE") == "1":
            tenant_id = "t_dev"
        else:
            host = request.headers.get("host", "")
            if "localhost" in host or "127.0.0.1" in host:
                tenant_id = "t_dev"
            else:
                tenant_id = self.extract_tenant_from_host(host)
        
        request.state.tenant_id = tenant_id
        
        response = await call_next(request)
        return response
    
    def extract_tenant_from_host(self, host: str) -> str:
        domain_mapping = {
            "schnittwerk.com": "t_schnittwerk",
            "app-fpsvflzd.fly.dev": "t_dev",
            "github-connector-app-lappw1a5.devinapps.com": "t_dev"
        }
        return domain_mapping.get(host, "t_dev")

def get_tenant_id(request: Request) -> str:
    return getattr(request.state, "tenant_id", "t_dev")
