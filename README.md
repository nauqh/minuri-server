# Minuri Server

<div align="center">
  <img src="./favicon.png" width="300" alt="Minuri icon">
</div>
<br/>
<p align="center">
<a href=""><img src="https://img.shields.io/badge/Latest%20Version-V0.1.0-blue.svg?&style=for-the-badge&logo=git&logoColor=white&colorB=7289DA"></a> <br>
<a href=""><img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"></a>
<a href=""><img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"></a>
<a href=""><img src="https://img.shields.io/badge/uv-%23DE5FE9.svg?style=for-the-badge&logo=uv&logoColor=white"></a> <br>
<a href=""><img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"></a>
<a href=""><img src="https://img.shields.io/badge/AWS_S3-FF9900?style=for-the-badge&logo=amazons3&logoColor=white"></a>
<a href=""><img src="https://img.shields.io/badge/SerpApi-2A6DF4?style=for-the-badge&logo=google&logoColor=white"></a>
<a href=""><img src="https://img.shields.io/badge/pydantic-%23E92063.svg?style=for-the-badge&logo=pydantic&logoColor=white"></a>
</p>

Minuri Server is the backend service for Minuri. It is built with FastAPI and currently powers APIs for location-based discovery and supporting data. Guide metadata exists in Postgres (`topics`, `arcs`; ORM also defines `guides` / `guide_sections` for future use), while markdown-style guide payloads live as JSON under `app/s3/guides-content/` and can be synced to S3 separately. The backend is expected to evolve over time, so this README is intentionally focused on local development and the current shape of the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Local Development](#local-development)
- [Docker](#docker)
- [Environment Variables](#environment-variables)
- [Data Sources and Import](#data-sources-and-import)
- [Data Flow](#data-flow)
- [Project Structure](#project-structure)
- [Current API Overview](#current-api-overview)
- [Notes](#notes)

## Getting Started

```bash
cd minuri-server
uv sync
```

Create a local `.env` file in the project root. For API-only development you only need the first two variables; add the AWS entries when running `sync_s3_content`.

```env
SERPAPI_API_KEY=your_key_here
DB_CONNECTION=postgresql://user:password@host/dbname?sslmode=require
# Optional — only needed for guide sync to S3
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_DEFAULT_REGION=ap-southeast-2
AWS_S3_BUCKET_NAME=your_bucket_name
```

Start the development server:

```bash
uv run uvicorn app.main:app --reload
```

## Local Development

- Server URL: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`
- Root endpoint: `http://127.0.0.1:8000/` (returns `{"message": "Root endpoint"}`)

The packaged project version is declared in `pyproject.toml` (`0.1.0`). The FastAPI app’s OpenAPI metadata still reports `version="0.0.1"` in `app/main.py`.

## Docker

From the repo root (requires Docker):

```bash
docker build -t minuri-server .
docker run --rm -p 8000:80 --env-file .env minuri-server
```

The image installs dependencies with `uv sync --frozen` and starts the app with `fastapi run app/main.py` on port 80 inside the container (mapped to `8000` in the example).

## Environment Variables

### Required for the API (`app/config.py`)

These are loaded via Pydantic Settings from `.env` (or the process environment):

| Variable | Purpose |
|----------|---------|
| `SERPAPI_API_KEY` | API key for nearby-interest search (SerpApi) |
| `DB_CONNECTION` | PostgreSQL connection string |

### Used by `sync_s3_content` only

The sync script loads `.env` with `python-dotenv` and uses boto3’s default credential chain plus:

| Variable | Purpose |
|----------|---------|
| `AWS_S3_BUCKET_NAME` | S3 bucket name (required by the script) |
| `AWS_DEFAULT_REGION` | Region passed to the S3 client |
| `AWS_ACCESS_KEY_ID` | AWS credentials (if not using another boto3 credential source) |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials (if not using another boto3 credential source) |

Keep secrets in your local `.env` file and do not commit them to source control.

## Data Sources and Import

This project combines suburb master data, official ABS population statistics, SerpApi for live nearby search, seeded topics/arcs metadata, and optional AWS S3 sync for guide JSON authored under `app/s3/`.

### Running database ETL scripts together

To reset the database and reload suburb demographics, suburb rows, and static reference data in one step:

```bash
uv run python -m app.scripts
```

This drops and recreates all tables defined on the SQLAlchemy `Base`, then runs these modules **in order**:

1. `app.scripts.extract` — ABS Excel → `app/data/victoria_population_table.csv`
2. `app.scripts.load_population_records` — CSV → `suburb_demographics`
3. `app.scripts.load_melbourne_suburbs` — Australian postcodes → `suburbs`
4. `app.scripts.seed_static_reference_data` — upsert `topics` and `arcs`

**Not included:** `app.scripts.sync_s3_content` (AWS sync). Run that separately when you need to push local guide JSON to S3.

---

### 1) Australian Postcodes (suburb master data)

Source:
- Repository: [https://github.com/matthewproctor/australianpostcodes](https://github.com/matthewproctor/australianpostcodes)
- CSV used by the loader: [https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/australian_postcodes.csv](https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/australian_postcodes.csv)

What it is:
- A structured postcode/locality dataset for Australia.

What it contains (used fields):
- Locality name, postcode, state
- Latitude/longitude
- SA2 code and SA3 name metadata

How we use it:
- `app.scripts.load_melbourne_suburbs` fetches the CSV, filters to Victoria suburbs in Greater Melbourne (SA4 codes 206–214), and writes records into the `suburbs` table.
- `GET /suburb` and `GET /suburb/larger-region` read from this imported data.

Load command:
```bash
uv run python -m app.scripts.load_melbourne_suburbs
```

---

### 2) ABS Regional Population (Victoria)

Source:
- ABS Regional Population release (Table 2): [https://www.abs.gov.au/statistics/people/population/regional-population/2024-25#data-downloads](https://www.abs.gov.au/statistics/people/population/regional-population/2024-25#data-downloads)

What it is:
- Official Australian Bureau of Statistics regional population dataset.

What it contains (used fields):
- SA2/SA3/SA4/GCCSA names and codes
- ERP population values (2024 and 2025)
- Growth and density measures (change %, area, density)

How we use it:
- `app.scripts.extract` converts the ABS Excel table into `app/data/victoria_population_table.csv`.
- `app.scripts.load_population_records` loads the CSV into `suburb_demographics`.
- `GET /api/population` sums `erp_2025` across rows whose SA2/SA3/SA4/GCCSA **names** contain the requested string (case-insensitive substring match via SQL `ILIKE`).

Load commands:
```bash
uv run python -m app.scripts.extract
uv run python -m app.scripts.load_population_records
```

---

### 3) Static Reference Data (Topics & Arcs)

What it is:
- Seed data for the `topics` and `arcs` tables, which classify guide content.

What it contains:
- **Topics (5):** Food & Eating, Getting Around, Health & Wellbeing, Home & Admin, Social & Belonging
- **Arcs (3):** You Just Moved In (Week 1), Getting Set Up (Month 1), Finding Your Rhythm (Month 3)

How we use it:
- `app.scripts.seed_static_reference_data` upserts records by slug, so it is safe to run repeatedly.

Load command:
```bash
uv run python -m app.scripts.seed_static_reference_data
```

---

### 4) SerpApi (live nearby-interest search)

Source:
- SerpApi Google Maps API: [https://serpapi.com/](https://serpapi.com/)

What it is:
- A live third-party search API used at request time.

What it contains:
- Nearby place results from Google Maps (names, ratings, addresses, open hours, thumbnails, GPS coordinates, and related listing metadata).

How we use it:
- `app.services.near_me` calls SerpApi using the `google_maps` engine with a Melbourne-area viewport (`ll`) and a query derived from suburb name plus topic/subtype (see `QUERY_MAP` and fallbacks in `app/services/near_me.py`).
- `GET /api/nearby-interest` returns live results directly from SerpApi (this flow does not persist data in the project database).
- Result count is whatever SerpApi returns for that search (there is **no** `start`/pagination parameter on this endpoint).

---

### 5) AWS S3 (guide content)

Source:
- Local files under `app/s3/` (guide JSON lives under `app/s3/guides-content/` by topic folders).

What it is:
- A sync script that mirrors local guide content files to an S3 bucket.

How we use it:
- `app.scripts.sync_s3_content` walks `app/s3/` recursively, compares MD5 hashes of local files against S3 ETags, and uploads only new or changed files using keys under the `guides-content/` prefix in the configured bucket.

Sync command:
```bash
uv run python -m app.scripts.sync_s3_content
```

---

## Data Flow

```mermaid
flowchart TD
    A1[Australian Postcodes CSV<br/>GitHub source] --> S3[load_melbourne_suburbs.py]
    A2[ABS Victoria Population XLSX] --> S1[extract.py]
    S1 --> F1[app/data/victoria_population_table.csv]
    F1 --> S2[load_population_records.py]
    S4[seed_static_reference_data.py] --> DB[(Postgres - Neon DB)]
    S3 --> DB
    S2 --> DB

    L1[app/s3/ local files] --> S5[sync_s3_content.py]
    S5 --> S3B[(AWS S3<br/>guides-content/)]

    RUN[python -m app.scripts<br/>ETL only — no S3 sync] --> S1
    RUN --> S2
    RUN --> S3
    RUN --> S4

    DB --> SV1[suburb_service.py]
    DB --> SV2[population_service.py]
    A3[SerpApi<br/>Google Maps Search] --> SV3[near_me.py]
    SV1 --> API[FastAPI app]
    SV2 --> API
    SV3 --> API

    API --> R1[GET /suburb]
    API --> R2[GET /suburb/larger-region]
    API --> R3[GET /api/population]
    API --> R4[GET /api/nearby-interest]
    R1 --> U[Client / Frontend]
    R2 --> U
    R3 --> U
    R4 --> U

    classDef source fill:#e3f2fd,stroke:#1e88e5,color:#0d47a1;
    classDef etl fill:#ede7f6,stroke:#5e35b1,color:#311b92;
    classDef db fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20;
    classDef serve fill:#fff3e0,stroke:#ef6c00,color:#e65100;
    classDef client fill:#fce4ec,stroke:#c2185b,color:#880e4f;
    classDef runner fill:#f3e5f5,stroke:#8e24aa,color:#4a148c;

    class A1,A2,A3,F1,L1 source;
    class S1,S2,S3,S4,S5 etl;
    class DB,S3B db;
    class SV1,SV2,SV3,R1,R2,R3,R4,API serve;
    class U client;
    class RUN runner;
```

### ERD

```mermaid
erDiagram
    TOPIC ||--o{ GUIDE : classifies
    ARC ||--o{ GUIDE : groups
    GUIDE ||--o{ GUIDE_SECTION : contains
    GUIDE ||--o| GUIDE : next_guide
    SUBURB_DEMOGRAPHIC ||--o{ SUBURB : maps_sa2

    TOPIC {
      int id PK
      string slug UK
      string name
      int sort_order
      boolean is_active
    }

    ARC {
      int id PK
      string slug UK
      string name
      int sort_order
      string timeframe_label
    }

    GUIDE {
      int id PK
      string title
      string slug UK
      int arc_id FK
      int arc_order
      int topic_id FK
      int next_guide_id FK
      string near_me_deeplink
      int reading_time_min
      boolean is_published
      boolean is_featured
      datetime created_at
      datetime updated_at
    }

    GUIDE_SECTION {
      int id PK
      int guide_id FK
      string section_key
      int section_order
      text body
      datetime updated_at
    }

    SUBURB {
      int id PK
      string name
      string postcode
      string state
      float lat
      float lng
      string sa2_code FK
      string sa3_name
    }

    SUBURB_DEMOGRAPHIC {
      int id PK
      string sa2_code UK
      string sa2_name
      string sa3_name
      string sa4_name
      string gccsa_name
      int erp_2024
      int erp_2025
      int erp_change_no
      float erp_change_pct
      float area_km2
      float pop_density_2025
    }
```

## Project Structure

```
minuri-server/
├── pyproject.toml
├── Dockerfile
├── app/
│   ├── main.py                            # FastAPI app, CORS config
│   ├── config.py                          # Settings (Pydantic, lru_cache)
│   ├── database.py                        # SQLAlchemy engine + session
│   ├── models.py                          # ORM models (Topic, Arc, Guide, GuideSection, Suburb, SuburbDemographic)
│   ├── routers/
│   │   ├── api.py                         # /api/nearby-interest, /api/population
│   │   └── suburb.py                      # /suburb, /suburb/larger-region
│   ├── schemas/
│   │   ├── near_me.py                     # NearbyInterest response schemas
│   │   └── suburb.py                      # Suburb response schemas
│   ├── services/
│   │   ├── near_me.py                     # SerpApi Google Maps search
│   │   ├── population_service.py          # Population aggregation
│   │   └── suburb_service.py              # Suburb queries
│   ├── scripts/
│   │   ├── __main__.py                    # Master runner (reset DB + ETL scripts; no S3 sync)
│   │   ├── extract.py                     # ABS Excel → CSV
│   │   ├── load_melbourne_suburbs.py      # Download & load suburb data
│   │   ├── load_population_records.py     # Load demographics CSV → DB
│   │   ├── seed_static_reference_data.py  # Seed Topics & Arcs
│   │   └── sync_s3_content.py             # Sync app/s3/** → AWS S3 guides-content/
│   ├── data/                              # CSV/XLSX inputs & generated CSV (ABS pipeline)
│   └── s3/
│       └── guides-content/                # Guide JSON grouped by topic slug folders
```

## Current API Overview

- `GET /`
- `GET /api/nearby-interest`
- `GET /api/population`
- `GET /suburb`
- `GET /suburb/larger-region`

### Nearby Interest

- **GET `/api/nearby-interest`**
  - Query params:
    - `suburb` (required) — suburb name passed through to the SerpApi query (`… near {suburb}`)
    - `topic` (optional) — one of `food-eating`, `getting-around`, `health-wellbeing`, `home-admin`, `social-belonging`; omit entirely for a default food-focused query
    - `subtype` (optional) — narrows the mapped search phrase when paired with `topic`. Supported pairs match `QUERY_MAP` in `app/services/near_me.py`:
      - **food-eating:** `food-dining`, `groceries`
      - **getting-around:** `public-transit`, `cycling`
      - **health-wellbeing:** `gp-clinics`, `mental-health`
      - **home-admin:** `services`, `libraries`
      - **social-belonging:** `community-spaces`, `social-venues`
      - Use `all` or omit `subtype` to use the per-topic fallback query string.
  - Response: `{ "suburb", "query", "results": [{ title, rating, reviews, address, type, price, open_state, description, thumbnail, place_id, gps_coordinates: { latitude, longitude } | null }] }`
  - Errors: 400 for invalid topic, 502 if SerpApi fails

### Population

- **GET `/api/population`**
  - Query params:
    - `location` (required) — case-insensitive substring match (`ILIKE`) against SA2, SA3, SA4, and GCCSA names in `suburb_demographics`; response is the sum of `erp_2025` over all matching rows
  - Response: `{ "population": <sum of erp_2025>, "location", "year": "2025" }`

### Suburb Endpoints

- **GET `/suburb`**
  - Query params:
    - `larger_region` (optional) — filter by SA3 name
  - Response: `{ "suburbs": [{ locality, postcode, state, long, lat, larger_region }] }`

- **GET `/suburb/larger-region`**
  - Returns all distinct SA3 names from suburb records.
  - Response: `{ "larger_regions": ["Bayside", "Melbourne City", "..."] }`

## Notes

- This backend is still early-stage and expected to evolve.
- Some endpoints depend on third-party APIs and external data sources.
- Frontend and backend integration details may shift as Minuri expands.
- `user-hub.md` in the repo root documents the web app’s User Hub drawer UX; it is not read by this server.
