"""
Load Victoria population CSV data into the suburb_demographics table.

Run from repo root:
  uv run python -m app.scripts.load_population_records
"""

import csv
from pathlib import Path

from app.database import SessionLocal
from app.models import SuburbDemographic

SOURCE_CSV_PATH = Path(__file__).resolve(
).parents[1] / "data" / "victoria_population_table.csv"


def _text_cell(raw: str | None) -> str:
    return (raw or "").strip()


def _int_cell(raw: str | None) -> int | None:
    value = _text_cell(raw)
    if value == "":
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def _float_cell(raw: str | None) -> float | None:
    value = _text_cell(raw)
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def load_rows(reader: csv.DictReader) -> list[dict]:
    payload: list[dict] = []
    for row in reader:
        sa2_code = _text_cell(row.get("sa2_code"))
        if not sa2_code:
            continue

        payload.append(
            {
                "sa2_code": sa2_code,
                "sa2_name": _text_cell(row.get("sa2_name")),
                "sa3_name": _text_cell(row.get("sa3_name")),
                "sa4_name": _text_cell(row.get("sa4_name")),
                "gccsa_name": _text_cell(row.get("gccsa_name")),
                "erp_2024": _int_cell(row.get("erp_2024")),
                "erp_2025": _int_cell(row.get("erp_2025")),
                "erp_change_no": _int_cell(row.get("erp_change_no")),
                "erp_change_pct": _float_cell(row.get("erp_change_pct")),
                "area_km2": _float_cell(row.get("area_km2")),
                "pop_density_2025": _float_cell(row.get("pop_density_2025")),
            }
        )
    return payload


def main() -> None:
    with SOURCE_CSV_PATH.open(mode="r", encoding="utf-8", newline="") as csv_file:
        payload = load_rows(csv.DictReader(csv_file))

    session = SessionLocal()
    try:
        session.query(SuburbDemographic).delete(synchronize_session=False)
        session.bulk_insert_mappings(SuburbDemographic, payload)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print(f"Inserted {len(payload)} suburb demographics records.")


if __name__ == "__main__":
    main()
