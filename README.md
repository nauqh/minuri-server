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

## Project Structure

- `app/main.py` - FastAPI application setup
- `app/routers/` - API route definitions
- `app/services/` - business logic and third-party data access
- `app/config.py` - settings and environment loading

## Current API Overview

- `GET /`
- `GET /api/nearby-interest`
- `GET /api/population`
- `GET /api/get-Suburb`

These routes reflect the current backend surface and may change as the project grows.

## Notes

- This backend is still early-stage and expected to evolve.
- Some endpoints depend on third-party APIs and external data sources.
- Frontend and backend integration details may shift as Minuri expands.
