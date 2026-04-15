import serpapi

from ..config import get_settings


class NearMeServiceError(Exception):
    pass


def fetch_nearby_interest(query: str, location: str) -> list[dict[str, str]]:
    """
    Fetch nearby interest details from SerpApi Google Local results.

    Example:
    query="Museum near Melbourne", location="Melbourne, Victoria, Australia"
    """
    settings = get_settings()
    client = serpapi.Client(api_key=settings.serpapi_api_key)
    payload = client.search(
        {
            "engine": "google",
            "q": query,
            "location": location,
            "gl": "au",
            "google_domain": "google.com.au",
            "tbm": "lcl",
        }
    )
    return payload["local_results"]


def search_near_me(query: str, location: str = "Melbourne"):
    try:
        return fetch_nearby_interest(query, location)
    except Exception as exc:
        raise NearMeServiceError(str(exc)) from exc
