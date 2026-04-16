# Minuri Server

<div align="center">
  <img src="./favicon.png" width="300" alt="Minuri icon">
</div>
<br/>
<p align="center">
<a href=""><img src="https://img.shields.io/badge/Latest%20Version-V0.0.1-blue.svg?&style=for-the-badge&logo=git&logoColor=white&colorB=7289DA"></a> <br>
<a href=""><img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"></a>
<a href=""><img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"></a>
<a href=""><img src="https://img.shields.io/badge/uv-%23DE5FE9.svg?style=for-the-badge&logo=uv&logoColor=white"></a> <br>
<a href=""><img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"></a>
<a href=""><img src="https://img.shields.io/badge/SerpApi-2A6DF4?style=for-the-badge&logo=google&logoColor=white"></a>
<a href=""><img src="https://img.shields.io/badge/pydantic-%23E92063.svg?style=for-the-badge&logo=pydantic&logoColor=white"></a>
</p>

Minuri Server is the backend service for Minuri. It is built with FastAPI and currently powers APIs for location-based discovery and supporting data. The backend is expected to evolve over time, so this README is intentionally focused on local development and the current shape of the project.

## Getting Started

```bash
cd minuri-server
uv sync
```

Create a local `.env` file in the project root:

```env
SERPAPI_API_KEY=your_key_here
```

Start the development server:

```bash
uv run uvicorn app.main:app --reload
```

## Local Development

- Server URL: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`
- Root endpoint: `http://127.0.0.1:8000/`

## Environment Variables

- `SERPAPI_API_KEY`: API key used for nearby-interest search

Keep secrets in your local `.env` file and do not commit them to source control.

## Data Sources and Import

This project currently uses three main external data sources: one for suburb master data, one for official population statistics, and one live API source for nearby places.

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
- `app.scripts.load_melbourne_suburbs` fetches the CSV, filters to Victoria suburbs in Greater Melbourne (`sa4` 206-214), and writes records into the `suburbs` table.
- `GET /suburb` and `GET /suburb/larger-region` read from this imported data.

Load command:
```bash
uv run python -m app.scripts.load_melbourne_suburbs
```

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
- `GET /api/population` aggregates `erp_2025` values by matching the requested location against SA2/SA3/SA4/GCCSA names.

Load commands:
```bash
uv run python -m app.scripts.extract
uv run python -m app.scripts.load_population_records
```

### 3) SerpApi (live nearby-interest search)

Source:
- SerpApi Google Local results API: [https://serpapi.com/](https://serpapi.com/)

What it is:
- A live third-party search API used at request time.

What it contains:
- Nearby place results from Google Local (for example, names, ratings, addresses, and related listing metadata).

How we use it:
- `app.services.near_me` calls SerpApi using `SERPAPI_API_KEY`.
- `GET /api/nearby-interest` returns live results directly from SerpApi (this flow does not persist data in the project database).

## Data Flow

The diagram below shows the main data sources for the app and how each source flows through loaders/services into the database and API endpoints.

```mermaid
flowchart TD
    A1[Australian Postcodes CSV<br/>GitHub source] --> B1[load_melbourne_suburbs.py]
    A2[ABS Victoria Population XLSX] --> B2[extract.py]
    B2 --> A3[victoria_population_table.csv]
    A3 --> B3[load_population_records.py]

    B1 --> DB[(Postgres / Neon DB)]
    B3 --> DB

    DB --> S1[suburb_service.py]
    DB --> S2[population_service.py]
    A4[SerpApi<br/>Google Local Search] --> S3[near_me.py]

    S1 --> API[FastAPI app]
    S2 --> API
    S3 --> API

    API --> R1[suburb routes]
    API --> R2[api/population]
    API --> R3[api/nearby-interest]
    R1 --> U[Client / Frontend]
    R2 --> U
    R3 --> U

    classDef source fill:#e3f2fd,stroke:#1e88e5,color:#0d47a1;
    classDef etl fill:#ede7f6,stroke:#5e35b1,color:#311b92;
    classDef db fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20;
    classDef serve fill:#fff3e0,stroke:#ef6c00,color:#e65100;
    classDef client fill:#fce4ec,stroke:#c2185b,color:#880e4f;

    class A1,A2,A3,A4 source;
    class B1,B2,B3 etl;
    class DB db;
    class S1,S2,S3,R1,R2,R3,API serve;
    class U client;
```

### ERD

![ERD](./ERD.svg)

## Project Structure

- `app/main.py` - FastAPI application setup
- `app/routers/` - API route definitions
- `app/services/` - business logic and third-party data access
- `app/config.py` - settings and environment loading

## Current API Overview

- `GET /`
- `GET /api/nearby-interest`
- `GET /api/population`
- `GET /suburb`
- `GET /suburb/larger-region`

These routes reflect the current backend surface and may change as the project grows.

### Suburb Endpoints

- `GET /suburb`
  - Query params:
    - `limit` (optional, default `100`, min `1`, max `1000`)
    - `larger_region` (optional SA3 name filter)
  - Response:
    - `{ "suburbs": [{ "locality", "postcode", "state", "long", "lat", "larger_region" }] }`
- `GET /suburb/larger-region`
  - Returns all distinct SA3 names from suburb records.
  - Response:
    - `{ "larger_regions": ["Bayside", "Melbourne City", "..."] }`

## Notes

- This backend is still early-stage and expected to evolve.
- Some endpoints depend on third-party APIs and external data sources.
- Frontend and backend integration details may shift as Minuri expands.
