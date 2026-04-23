"""
Seed static reference data for Iteration 2.

This script is idempotent: it upserts by `slug`.

Run from repo root:
  uv run python -m app.scripts.seed_static_reference_data
"""

from collections.abc import Sequence

from app.database import SessionLocal
from app.models import Arc, Topic

TOPICS: list[dict[str, object]] = [
    {"slug": "food_eating", "name": "Food & Eating",
        "sort_order": 1, "is_active": True},
    {"slug": "getting_around", "name": "Getting Around",
        "sort_order": 2, "is_active": True},
    {"slug": "health_wellbeing", "name": "Health & Wellbeing",
        "sort_order": 3, "is_active": True},
    {"slug": "home_admin", "name": "Home & Admin",
        "sort_order": 4, "is_active": True},
    {"slug": "social_belonging", "name": "Social & Belonging",
        "sort_order": 5, "is_active": True},
]

ARCS: list[dict[str, object]] = [
    {
        "slug": "week_one",
        "name": "You Just Moved In",
        "sort_order": 1,
        "timeframe_label": "Week 1",
    },
    {
        "slug": "month_one",
        "name": "Getting Set Up",
        "sort_order": 2,
        "timeframe_label": "Month 1",
    },
    {
        "slug": "month_three",
        "name": "Finding Your Rhythm",
        "sort_order": 3,
        "timeframe_label": "Month 3",
    },
]


def _upsert_by_slug(session, model, rows: Sequence[dict[str, object]]) -> int:
    existing = {
        getattr(item, "slug"): item
        for item in session.query(model).all()
    }

    inserted = 0
    for row in rows:
        slug = str(row["slug"])
        current = existing.get(slug)
        if current is None:
            session.add(model(**row))
            inserted += 1
            continue

        for key, value in row.items():
            setattr(current, key, value)

    return inserted


def main() -> None:
    session = SessionLocal()
    try:
        inserted_topics = _upsert_by_slug(session, Topic, TOPICS)
        inserted_arcs = _upsert_by_slug(session, Arc, ARCS)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print(
        f"Seeded topics: total={len(TOPICS)}, inserted={inserted_topics}, "
        f"updated={len(TOPICS) - inserted_topics}"
    )
    print(
        f"Seeded arcs: total={len(ARCS)}, inserted={inserted_arcs}, "
        f"updated={len(ARCS) - inserted_arcs}"
    )


if __name__ == "__main__":
    main()
