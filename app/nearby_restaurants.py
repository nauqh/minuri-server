from __future__ import annotations

from typing import Any

import serpapi
import json
from app.config import get_settings


MELBOURNE_SCOPE = "Melbourne, Victoria, Australia"


def fetch_place_details_serpapi(
    query: str,
    location: str = MELBOURNE_SCOPE,
) -> list[dict[str, Any]]:
    """
    Fetch richer nearby place details from SerpApi Google Local results.

    Example:
    query="Restaurant in Carlton", location="Melbourne, Victoria, Australia"
    """
    settings = get_settings()

    client = serpapi.Client(api_key=settings.serpapi_api_key)
    payload = client.search(
        {
            "engine": "google_local",
            "q": query,
            "location": location,
            "num": settings.default_limit,
        }
    )
    local_results = payload["local_results"]
    with open("local_results.json", "w") as f:
        json.dump(local_results, f)
    return local_results


def run_simple_demo() -> None:

    place_details = fetch_place_details_serpapi(
        query="Korean Cafe near Overlay",
    )
    for idx, place in enumerate(place_details, start=1):
        print(
            f"{idx}. {place.get('title')} | {place.get('address')} | "
            f"rating={place.get('rating')} ({place.get('reviews')} reviews) | {place.get('thumbnail')}"
        )


if __name__ == "__main__":
    run_simple_demo()
