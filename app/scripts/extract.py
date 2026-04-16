"""
Extracts the population data from the Victoria Population Table 2 Excel file.

Ref: https://www.abs.gov.au/statistics/people/population/regional-population/2024-25#data-downloads

Run from repo root:
  uv run python -m app.scripts.extract
"""

import pandas as pd

INPUT_FILE = "32180DS0001_2024-25.xlsx"
OUTPUT_FILE = "app/data/victoria_population_table.csv"
SHEET = "Table 2"

df = pd.read_excel("app/data/" + INPUT_FILE, sheet_name=SHEET,
                   header=None, skiprows=5)

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

# Drop non-data rows (subtotals, blanks, footnotes)
df = df[
    pd.to_numeric(df["sa2_code"], errors="coerce").notna()
].reset_index(drop=True)

df.to_csv(OUTPUT_FILE, index=False)
print(f"Saved {len(df)} rows to {OUTPUT_FILE}")
