from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import get_settings

router = APIRouter(tags=["About"])

class AppInfo(BaseModel):
    app_name: str
    edition: str
    version: str
    brand: str
    creator: str
    footer: str

@router.get("/info", response_model=AppInfo)
def info():
    s = get_settings()
    return AppInfo(app_name=s.app_name, edition=s.edition, version=s.version, brand=s.brand, creator=s.creator, footer=f"{s.app_name} v{s.version}")
