from pydantic import BaseModel


class NearMeCoordinatesResponse(BaseModel):
    latitude: float | None = None
    longitude: float | None = None


class NearbyInterestItemResponse(BaseModel):
    title: str | None = None
    rating: float | None = None
    reviews: int | None = None
    address: str | None = None
    type: str | None = None
    price: str | None = None
    open_state: str | None = None
    description: str | None = None
    thumbnail: str | None = None
    place_id: str | None = None
    gps_coordinates: NearMeCoordinatesResponse | None = None


class NearbyInterestListResponse(BaseModel):
    suburb: str
    query: str
    results: list[NearbyInterestItemResponse]
