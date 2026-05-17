from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

GuideTopicSlug = Literal[
    "food-eating",
    "getting-around",
    "health-wellbeing",
    "home-admin",
    "social-belonging",
]

SpeciesKey = Literal["pioneer", "settler", "builder", "openheart"]


class VibeLLM(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="2-3 word poetic name, e.g. 'Lavender Calm'")
    hex: str = Field(description="Vivid saturated hex color readable on white, e.g. '#9B8EC4'. No near-white, near-black, or grey.")
    traits: str = Field(description="Short comma-separated trait line, e.g. 'Reflective, creative, emotionally self-aware.'")


class IdentityLLM(BaseModel):
    model_config = ConfigDict(extra="forbid")

    species: SpeciesKey = Field(description="One of: pioneer, settler, builder, openheart")
    vibe: VibeLLM
    letter_body: str = Field(description="Personalized 2-3 sentence letter body about their Melbourne journey. Second person, warm but not saccharine.")
    suburb_line: str = Field(description="One line about the suburb, e.g. 'Fitzroy: your new corner of Melbourne.'")


class DayPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day: int = Field(ge=1, le=7)
    theme: str = Field(description="Short day theme, e.g. 'Survive & Land'")
    short_label: str = Field(description="Stepper nav label, max 8 characters")
    narrative: str = Field(description="1-2 sentences personalized to the user's moment. Not generic advice.")
    primary_topic: GuideTopicSlug
    secondary_topics: Annotated[list[GuideTopicSlug], Field(max_length=1)]
    primary_guides: Annotated[list[str], Field(min_length=1, max_length=2, description="Slugs from primary_topic only")]
    secondary_guides: Annotated[list[str], Field(max_length=1, description="Slugs from secondary_topics only")]
    tasks: Annotated[list[str], Field(min_length=1, max_length=2, description="Concrete action sentences, specific to the user's situation")]
    memory_line: str = Field(description="Past-tense, max 12 words. Stored on identity card when day is completed.")
    stamp_label: Optional[str] = Field(default=None, description="Badge label if day earns a stamp. Only set for days 1 and 7. Null for all other days.")


class WeekPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    days: Annotated[list[DayPlan], Field(min_length=7, max_length=7)]


class JourneyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identity: IdentityLLM
    week_plan: WeekPlan


class JourneyRequest(BaseModel):
    suburb: str
    your_moment: str
    selected_topics: list[GuideTopicSlug]
