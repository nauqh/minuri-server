from pydantic import BaseModel


class SuburbItemResponse(BaseModel):
    locality: str
    postcode: str | None
    state: str
    long: float | None
    lat: float | None
    larger_region: str | None


class SuburbListResponse(BaseModel):
    suburbs: list[SuburbItemResponse]


class LargerRegionListResponse(BaseModel):
    larger_regions: list[str]
