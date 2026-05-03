import re
import serpapi

from ..config import get_settings


class NearMeServiceError(Exception):
    pass


VALID_TOPICS = {
    "food-eating",
    "getting-around",
    "health-wellbeing",
    "home-admin",
    "social-belonging",
}

QUERY_MAP: dict[tuple[str, str], str] = {
    ("food-eating", "food-dining"): "cheap restaurants cafes food",
    ("food-eating", "groceries"): "supermarkets grocery stores",
    ("getting-around", "public-transit"): "train station tram stop",
    ("getting-around", "cycling"): "bus stop bicycle hire station",
    ("health-wellbeing", "gp-clinics"): "GP medical centre bulk billing clinic",
    ("health-wellbeing", "mental-health"): "psychologist counsellor mental health service",
    ("home-admin", "services"): "government services community centre settlement support",
    ("home-admin", "libraries"): "public library",
    ("social-belonging", "community-spaces"): "park community centre multicultural centre free",
    ("social-belonging", "social-venues"): "bar pub social club",
}

_TOPIC_FALLBACK: dict[str, str] = {
    "food-eating": "cheap restaurants cafes groceries food",
    "getting-around": "train tram bus stop bicycle hire station",
    "health-wellbeing": "GP medical centre bulk billing clinic mental health",
    "home-admin": "government services community centre library",
    "social-belonging": "park community centre bar pub social club",
}

_DEFAULT_QUERY = "cheap restaurants cafes food"


def resolve_query(topic: str | None, subtype: str | None) -> str:
    if topic is None:
        return _DEFAULT_QUERY
    if subtype is None or subtype == "all":
        return _TOPIC_FALLBACK.get(topic, _DEFAULT_QUERY)
    return QUERY_MAP.get((topic, subtype), _TOPIC_FALLBACK.get(topic, _DEFAULT_QUERY))


def _extract_places(payload: dict) -> list[dict]:
    local_results = payload.get("local_results", [])
    if isinstance(local_results, dict):
        places = local_results.get("places", [])
        return places if isinstance(places, list) else []
    if isinstance(local_results, list):
        return local_results
    return []


def _upscale_thumbnail(url: str | None) -> str | None:
    if not url:
        return url
    # Google encodes size as =w128-h92-k-no; bump to 800×600 for clarity
    return re.sub(r"=w\d+-h\d+", "=w800-h600", url)


def _normalize_place(place: dict) -> dict:
    return {
        "title": place.get("title"),
        "rating": place.get("rating"),
        "reviews": place.get("reviews"),
        "address": place.get("address"),
        "type": place.get("type"),
        "price": place.get("price"),
        "open_state": place.get("hours"),
        "description": place.get("description"),
        "thumbnail": _upscale_thumbnail(place.get("thumbnail")),
        "place_id": place.get("place_id"),
        "gps_coordinates": place.get("gps_coordinates"),
    }


def search_near_me(
    suburb: str,
    topic: str | None = None,
    subtype: str | None = None,
) -> list[dict]:
    query = resolve_query(topic, subtype)
    try:
        search_query = f"{query} near {suburb}"
        settings = get_settings()
        client = serpapi.Client(api_key=settings.serpapi_api_key)
        payload = client.search(
            {
                "engine": "google_maps",
                "type": "search",
                "q": search_query,
                "ll": "@-37.8136,144.9631,12z",
                "hl": "en",
                "gl": "au",
            }
        )
        places = _extract_places(payload)
        return [_normalize_place(place) for place in places]
    except Exception as exc:
        raise NearMeServiceError(str(exc)) from exc


if __name__ == "__main__":
    try:
        import json
        items = search_near_me(suburb="Clayton South",
                               topic="food-eating", subtype="food-dining")
        with open("items.json", "w") as f:
            json.dump(items, f)
    except NearMeServiceError as exc:
        print(f"Search failed: {exc}")
