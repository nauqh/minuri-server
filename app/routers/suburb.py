from fastapi import APIRouter, Query

from ..database import DbSession
from ..schemas.suburb import SuburbListResponse
from ..services.suburb_service import get_suburb_service

router = APIRouter(
    prefix="/suburb",
    tags=["suburb"],
)


@router.get("", response_model=SuburbListResponse)
def list_suburbs(
    db: DbSession,
    limit: int = Query(100, ge=1, le=1000),
    larger_region: str | None = Query(None),
):
    return get_suburb_service(
        db,
        limit=limit,
        larger_region=larger_region,
    )
