from fastapi import APIRouter, HTTPException, Query

from ..database import DbSession
from ..schemas.near_me import NearbyInterestListResponse
from ..services.near_me import (
    VALID_TOPICS,
    NearMeServiceError,
    resolve_query,
    search_near_me,
)
from ..services.population_service import get_population_service

router = APIRouter(
    prefix="/api",
    tags=["near-me"],
)


@router.get("/nearby-interest", response_model=NearbyInterestListResponse)
async def get_nearby_interest(
    suburb: str = Query(..., min_length=1),
    topic: str | None = Query(None),
    subtype: str | None = Query(None),
):
    if topic is not None and topic not in VALID_TOPICS:
        raise HTTPException(status_code=400, detail=f"Invalid topic: '{topic}'")
    try:
        results = search_near_me(suburb=suburb, topic=topic, subtype=subtype)
        return {"suburb": suburb, "query": resolve_query(topic, subtype), "results": results}
    except NearMeServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/population")
async def get_population(
    db: DbSession,
    location: str,
):
    return get_population_service(db, location)
