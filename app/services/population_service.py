from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..models import SuburbDemographic


def get_population_service(db: Session, location: str) -> dict:
    location_query = location.strip()
    row = (
        db.query(func.sum(SuburbDemographic.erp_2025))
        .filter(
            or_(
                SuburbDemographic.sa2_name.ilike(f"%{location_query}%"),
                SuburbDemographic.sa3_name.ilike(f"%{location_query}%"),
                SuburbDemographic.sa4_name.ilike(f"%{location_query}%"),
                SuburbDemographic.gccsa_name.ilike(f"%{location_query}%"),
            )
        )
        .first()
    )

    population = int(row[0] or 0)
    return {
        "population": population,
        "location": location,
        "year": "2025",
    }
