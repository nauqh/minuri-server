from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from ..config import get_settings
from ..services.near_me import NearMeServiceError, search_near_me
from ..services.population_service import get_population_service

router = APIRouter(
    prefix="/api",
    tags=["near-me"],
)


@router.get("/nearby-interest")
async def get_nearby_interest(
    query: str = Query(..., min_length=1),
    location: str = Query("Melbourne"),
    mode: Literal["default"] = "default",
):
    _ = get_settings()
    try:
        return search_near_me(query=query, location=location)
    except NearMeServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/population")
async def get_population(location: str, year: str = 2026):
    return get_population_service(location, year)
