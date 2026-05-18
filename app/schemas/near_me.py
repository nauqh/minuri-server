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


class NearbyEventVenueResponse(BaseModel):
    name: str | None = None
    rating: float | None = None
    reviews: int | None = None


class NearbyEventDateResponse(BaseModel):
    start_date: str | None = None
    when: str | None = None


class NearbyEventResponse(BaseModel):
    title: str | None = None
    date: NearbyEventDateResponse | None = None
    address: list[str] | None = None
    description: str | None = None
    link: str | None = None
    thumbnail: str | None = None
    venue: NearbyEventVenueResponse | None = None


class NearbyEventListResponse(BaseModel):
    suburb: str
    query: str
    date_filter: str
    results: list[NearbyEventResponse]
