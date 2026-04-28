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
    by_sa2_code: dict[str, dict] = {}
    for row in reader:
        sa2_code = _text_cell(row.get("sa2_code"))
        if not sa2_code:
            continue

        parsed = {
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
        # Keep the last occurrence if duplicates appear in source.
        by_sa2_code[sa2_code] = parsed

    payload.extend(by_sa2_code.values())
    return payload


def main() -> None:
    with SOURCE_CSV_PATH.open(mode="r", encoding="utf-8", newline="") as csv_file:
        payload = load_rows(csv.DictReader(csv_file))
    if not payload:
        raise RuntimeError("No demographic rows parsed from source CSV.")

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

    with_erp_2025 = sum(1 for row in payload if row["erp_2025"] is not None)
    print(
        f"Inserted {len(payload)} suburb demographics records "
        f"({with_erp_2025} with ERP 2025 values)."
    )


if __name__ == "__main__":
    main()
