"""
Load Melbourne suburbs from the australianpostcodes source CSV.

Criteria: "state" = VIC and "sa4" in 206-214 (Greater Melbourne). 
Ref: https://archive.org/details/gccsa-2-gmel#:~:text=Note:%20Original%20Excel%20tables%20and%20csvs%20available%20in%20download%20options.%20206%20Melbourne%20%2D%20Inner&text=214%20Mornington%20Peninsula%2021401%20Frankston

Run from repo root:
  uv run python -m app.scripts.load_melbourne_suburbs
"""


import csv
import requests

from app.database import SessionLocal
from app.models import Suburb, SuburbDemographics

SOURCE_CSV_URL = (
    "https://raw.githubusercontent.com/matthewproctor/"
    "australianpostcodes/master/australian_postcodes.csv"
)
MELBOURNE_SA4_CODES = {str(n) for n in range(206, 215)}


def _float_cell(raw: str | None) -> float | None:
    if raw is None or raw.strip() == "":
        return None
    try:
        return float(raw.strip())
    except ValueError:
        return None


def _title_locality(raw: str) -> str:
    return raw.strip().title()


def load_rows(reader: csv.DictReader) -> list[dict]:
    payload: list[dict] = []
    for row in reader:
        if row.get("state") != "VIC":
            continue
        sa4 = (row.get("sa4") or "").strip()
        if sa4 not in MELBOURNE_SA4_CODES:
            continue
        payload.append(
            {
                "name": _title_locality(row.get("locality") or ""),
                "postcode": (row.get("postcode") or "").strip(),
                "state": "VIC",
                "lat": _float_cell(row.get("Lat_precise")) or _float_cell(row.get("lat")),
                "lng": _float_cell(row.get("Long_precise")) or _float_cell(row.get("long")),
                "sa4_name": (row.get("sa4name") or "").strip() or None,
            }
        )
    return payload


def main() -> None:
    # Download the CSV file from the source URL
    response = requests.get(SOURCE_CSV_URL, timeout=30)
    response.raise_for_status()

    # Split the CSV file into lines
    lines = response.text.splitlines()
    payload = load_rows(csv.DictReader(lines))
    session = SessionLocal()
    try:
        # Clear existing suburbs
        session.query(SuburbDemographics).delete(synchronize_session=False)
        session.query(Suburb).delete(synchronize_session=False)

        # Insert new suburbs
        session.bulk_insert_mappings(Suburb, payload)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print(f"Inserted {len(payload)} suburbs.")


if __name__ == "__main__":
    main()
