from fastapi import APIRouter, Query

from ..database import DbSession
from ..schemas.suburb import LargerRegionListResponse, SuburbListResponse
from ..services.suburb_service import get_larger_regions_service, get_suburb_service

router = APIRouter(
    prefix="/suburb",
    tags=["suburb"],
)


@router.get("", response_model=SuburbListResponse)
def list_suburbs(
    db: DbSession,
    larger_region: str | None = Query(None),
):
    return get_suburb_service(
        db,
        larger_region=larger_region,
    )


@router.get("/larger-region", response_model=LargerRegionListResponse)
def list_larger_regions(db: DbSession):
    return get_larger_regions_service(db)
