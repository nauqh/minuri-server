import serpapi

from ..config import get_settings


class NearMeServiceError(Exception):
    pass


def _extract_places(payload: dict) -> list[dict]:
    local_results = payload.get("local_results", [])
    if isinstance(local_results, dict):
        places = local_results.get("places", [])
        return places if isinstance(places, list) else []
    if isinstance(local_results, list):
        return local_results
    return []


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
        "thumbnail": place.get("thumbnail"),
        "place_id": place.get("place_id"),
        "gps_coordinates": place.get("gps_coordinates"),
    }


def search_near_me(query: str, suburb: str = "Melbourne") -> list[dict]:
    """
    Fetch nearby interest details from SerpApi Google Local results.

    Example:
    query="Cheap eats & groceries", suburb="Clayton South"
    """
    try:
        search_query = query if " near " in query.lower(
        ) else f"{query} near {suburb}"
        settings = get_settings()
        client = serpapi.Client(api_key=settings.serpapi_api_key)
        payload = client.search(
            {
                "engine": "google",
                "q": search_query,
                "location": "Melbourne, Victoria, Australia",
                "gl": "au",
                "google_domain": "google.com.au",
                "hl": "en",
                "device": "desktop",
            }
        )
        places = _extract_places(payload)
        return [_normalize_place(place) for place in places]
    except Exception as exc:
        raise NearMeServiceError(str(exc)) from exc


if __name__ == "__main__":
    test_suburb = "Clayton South"
    test_query = "cheap eats & groceries"

    try:
        import json
        items = search_near_me(query=test_query, suburb=test_suburb)
        with open("items.json", "w") as f:
            json.dump(items, f)
    except NearMeServiceError as exc:
        print(f"Search failed: {exc}")
