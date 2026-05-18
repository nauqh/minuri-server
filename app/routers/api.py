from fastapi import APIRouter, HTTPException, Query

from ..database import DbSession
from ..schemas.near_me import NearbyEventListResponse, NearbyInterestListResponse
from ..services.near_me import (
    VALID_DATE_FILTERS,
    VALID_TOPICS,
    NearMeServiceError,
    _DATE_FILTER_DEFAULT,
    resolve_query,
    search_near_me,
    search_near_me_events,
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


@router.get("/nearby-events", response_model=NearbyEventListResponse)
async def get_nearby_events(
    suburb: str = Query(..., min_length=1),
    date_filter: str = Query(_DATE_FILTER_DEFAULT),
):
    if date_filter not in VALID_DATE_FILTERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date_filter '{date_filter}'. Valid: {sorted(VALID_DATE_FILTERS)}",
        )
    try:
        results = search_near_me_events(suburb=suburb, date_filter=date_filter)
        return {
            "suburb": suburb,
            "query": f"social community events {suburb} Melbourne",
            "date_filter": date_filter,
            "results": results,
        }
    except NearMeServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/population")
async def get_population(
    db: DbSession,
    location: str,
):
    return get_population_service(db, location)
