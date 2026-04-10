import serpapi
import json
from config import get_settings

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
        }
    )
    return payload