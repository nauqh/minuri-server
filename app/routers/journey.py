from fastapi import APIRouter, HTTPException
from loguru import logger

from ..schemas.journey import JourneyRequest, JourneyResponse
from ..services.journey_service import get_journey_plan

router = APIRouter(
    prefix="/journey",
    tags=["journey"],
)


@router.post("", response_model=JourneyResponse)
async def create_journey(body: JourneyRequest):
    try:
        return get_journey_plan(
            suburb=body.suburb,
            your_moment=body.your_moment,
            selected_topics=body.selected_topics,
        )
    except Exception as exc:
        logger.error("Journey plan failed | suburb={} error={}", body.suburb, exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
