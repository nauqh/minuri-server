"""
Run all data scripts in sequence.

Run from repo root:
  uv run python -m app.scripts
"""

from __future__ import annotations

import subprocess
import sys

from loguru import logger

from app import models
from app.database import engine


MODULES = [
    "app.scripts.extract",
    "app.scripts.load_population_records",
    "app.scripts.load_melbourne_suburbs",
    "app.scripts.seed_static_reference_data",
]


def main() -> None:
    logger.info("[START] reset database schema")
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    logger.info("[DONE ] reset database schema")

    for module in MODULES:
        logger.info(f"[START] {module}")
        subprocess.run(
            [sys.executable, "-m", module],
            check=True,
        )
        logger.info(f"[DONE] {module}")

    logger.success("All scripts completed.")


if __name__ == "__main__":
    main()
