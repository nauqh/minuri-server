from fastapi import APIRouter

from ..database import DbSession
from ..schemas.suburb import SuburbListResponse
from ..services.suburb_service import get_suburb_service

router = APIRouter(
    prefix="/suburb",
    tags=["suburb"],
)


@router.get("", response_model=SuburbListResponse)
def list_suburbs(db: DbSession):
    return get_suburb_service(db)
