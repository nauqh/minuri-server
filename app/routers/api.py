from fastapi import APIRouter, HTTPException, Query

from ..database import DbSession
from ..schemas.near_me import NearbyInterestListResponse
from ..services.near_me import NearMeServiceError, search_near_me
from ..services.population_service import get_population_service

router = APIRouter(
    prefix="/api",
    tags=["near-me"],
)


@router.get("/nearby-interest", response_model=NearbyInterestListResponse)
async def get_nearby_interest(
    suburb: str = Query(..., min_length=1),
    query: str = Query("cheap eats & groceries", min_length=1),
):
    try:
        results = search_near_me(query=query, suburb=suburb)
        return {"suburb": suburb, "query": query, "results": results}
    except NearMeServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/population")
async def get_population(
    db: DbSession,
    location: str,
):
    return get_population_service(db, location)
