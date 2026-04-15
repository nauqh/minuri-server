import serpapi
import json
from app.config import get_settings

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
            "tbm": "lcl"
        }
    )
    res = payload["local_results"]
    return res