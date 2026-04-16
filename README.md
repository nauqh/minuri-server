# Minuri Server

Minuri Server is the backend service for Minuri. It is built with FastAPI and currently powers APIs for location-based discovery and supporting data. The backend is expected to evolve over time, so this README is intentionally focused on local development and the current shape of the project.

## Current Responsibilities

- Expose HTTP APIs for nearby-interest search
- Provide supporting population and suburb endpoints
- Act as the backend foundation for future Minuri features

## Tech Stack

- Python 3.11+
- FastAPI
- `uv`
- SerpApi
- `requests`
- `pydantic-settings`

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

## Suburb Data Source and Import

Suburb records are sourced from the `australianpostcodes` dataset by Matthew Proctor:

- Repository: [https://github.com/matthewproctor/australianpostcodes](https://github.com/matthewproctor/australianpostcodes)
- CSV used by the loader: [https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/australian_postcodes.csv](https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/australian_postcodes.csv)

Load suburbs into your DB with:

```bash
uv run python -m app.scripts.load_melbourne_suburbs
```

The loader fetches the CSV from the upstream source, filters to VIC suburbs in Greater Melbourne (`sa4` 206-214), clears existing suburb rows, then inserts the refreshed set.

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
