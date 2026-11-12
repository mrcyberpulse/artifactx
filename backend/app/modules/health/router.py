from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import get_settings

router = APIRouter(tags=["Health"])

class HealthStatus(BaseModel):
    status: str
    version: str
    edition: str

@router.get("/health", response_model=HealthStatus)
def health():
    s = get_settings()
    return HealthStatus(status="ok", version=s.version, edition=s.edition)
