import copy
import re
from pathlib import Path

import requests
from loguru import logger

from ..config import get_settings
from ..schemas.journey import GuideTopicSlug, JourneyResponse

GUIDES_BY_TOPIC = {
    "food-eating": [
        "cheap-eats-when-broke",
        "cooking-5-meals-youll-actually-eat",
        "finding-free-community-meals",
        "meal-prepping-on-a-tight-budget",
        "your-first-grocery-run",
    ],
    "getting-around": [
        "building-a-local-routine",
        "cycling-melbourne-without-fear",
        "finding-your-way-around-melbourne-in-week-one",
        "getting-myki-and-surviving-ptv",
        "night-transport-and-getting-home-safe",
    ],
    "health-wellbeing": [
        "crisis-lines-you-can-actually-call",
        "emergency-vs-urgent-care-in-melbourne",
        "finding-a-gp-before-you-need-one",
        "managing-your-prescriptions-in-a-new-city",
        "medicare-bulk-billing-and-mental-health-care-plans",
        "sustaining-yourself-sleep-movement-and-disconnecting",
        "when-to-see-a-psych-counsellor-or-friend",
        "your-pharmacist-is-the-cheapest-first-stop",
    ],
    "home-admin": [
        "budgeting-on-what-you-actually-earn",
        "renting-without-getting-burned",
        "setting-up-utilities-without-overpaying",
        "super-and-your-first-paycheck",
        "tenant-rights-when-things-go-wrong",
        "your-bond-starts-on-day-one",
        "your-first-48-hours-checklist",
    ],
    "social-belonging": [
        "finding-your-community",
        "free-things-to-do-this-week",
        "homesickness-nobody-warns-you-about",
        "making-friends-in-a-city-where-everyones-busy",
        "surviving-the-first-weekend-alone",
        "volunteering-as-a-way-in",
        "when-you-dont-know-anyone-yet",
    ],
}

SPECIES_DESCRIPTIONS = {
    "pioneer": "The Quiet Pioneer — independent, self-directed, roots slowly but deeply",
    "settler": "The Careful Settler — health-conscious, grounded, builds sustainable rhythms",
    "builder": "The Steady Builder — practical, admin-first, one thing sorted at a time",
    "openheart": "The Open Heart — socially driven, connection-seeking, warmth-first",
}

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
_PROMPT_PATH = Path(__file__).parent / "prompt.md"
_SYSTEM_PROMPT_TEMPLATE = _PROMPT_PATH.read_text()


def _sanitize_json(raw: str) -> str:
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", raw)


def _inline_refs(node: dict | list, defs: dict) -> dict | list:
    """Resolve $ref entries so strict mode doesn't choke on $defs."""
    if isinstance(node, list):
        return [_inline_refs(i, defs) for i in node]
    if not isinstance(node, dict):
        return node
    if "$ref" in node:
        ref_name = node["$ref"].split("/")[-1]
        return _inline_refs(copy.deepcopy(defs[ref_name]), defs)
    return {k: _inline_refs(v, defs) for k, v in node.items() if k != "$defs"}


_RAW_SCHEMA = JourneyResponse.model_json_schema()
_SCHEMA = _inline_refs(copy.deepcopy(_RAW_SCHEMA), _RAW_SCHEMA.get("$defs", {}))


def get_journey_plan(
    suburb: str,
    your_moment: str,
    selected_topics: list[GuideTopicSlug],
) -> JourneyResponse:
    logger.info("Generating journey plan | suburb={} topics={}", suburb, selected_topics)
    settings = get_settings()
    response = requests.post(
        url=_OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "openrouter/owl-alpha",
            "messages": [
                {
                    "role": "system",
                    "content": _SYSTEM_PROMPT_TEMPLATE.format(
                        suburb=suburb,
                        species_descriptions="\n".join(
                            f"- {k}: {v}" for k, v in SPECIES_DESCRIPTIONS.items()
                        ),
                        guides_by_topic="\n".join(
                            f"{topic}: {', '.join(slugs)}"
                            for topic, slugs in GUIDES_BY_TOPIC.items()
                        ),
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Suburb: {suburb}\n"
                        f'Moment: "{your_moment}"\n'
                        f"Priority topics: {selected_topics}\n\n"
                        "Generate identity and 7-day journey plan."
                    ),
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "journey_plan",
                    "strict": True,
                    "schema": _SCHEMA,
                },
            },
        },
        timeout=60,
    )
    response.raise_for_status()
    logger.debug("LLM response status={} suburb={}", response.status_code, suburb)
    content = response.json()["choices"][0]["message"]["content"]
    result = JourneyResponse.model_validate_json(_sanitize_json(content))
    logger.info("Journey plan generated | suburb={} species={}", suburb, result.identity.species)
    return result
