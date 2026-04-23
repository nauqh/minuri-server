"""
Extracts the population data from the Victoria Population Table 2 Excel file.

Ref: https://www.abs.gov.au/statistics/people/population/regional-population/2024-25#data-downloads

Run from repo root:
  uv run python -m app.scripts.extract
"""

import pandas as pd
from pathlib import Path

INPUT_FILE = "32180DS0001_2024-25.xlsx"
OUTPUT_FILE = "app/data/victoria_population_table.csv"
SHEET = "Table 2"

data_dir = Path(__file__).resolve().parents[1] / "data"
input_path = data_dir / INPUT_FILE
output_path = Path(OUTPUT_FILE)


def main() -> None:
    df = pd.read_excel(input_path, sheet_name=SHEET, header=None, skiprows=5)

    columns = [
        "gccsa_code", "gccsa_name",
        "sa4_code", "sa4_name",
        "sa3_code", "sa3_name",
        "sa2_code", "sa2_name",
        "erp_2024", "erp_2025",
        "erp_change_no", "erp_change_pct",
        "natural_increase", "net_internal_migration", "net_overseas_migration",
        "area_km2", "pop_density_2025"
    ]
    df.columns = columns

    # Keep only data rows with valid numeric SA2 codes.
    df = df[pd.to_numeric(df["sa2_code"], errors="coerce").notna()].copy()
    df["sa2_code"] = df["sa2_code"].astype(int).astype(str)

    # Keep only the columns required by DB loader.
    keep = [
        "sa2_code",
        "sa2_name",
        "sa3_name",
        "sa4_name",
        "gccsa_name",
        "erp_2024",
        "erp_2025",
        "erp_change_no",
        "erp_change_pct",
        "area_km2",
        "pop_density_2025",
    ]
    df = df[keep].drop_duplicates(
        subset=["sa2_code"], keep="last").reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} rows to {output_path}")


if __name__ == "__main__":
    main()
