from sqlalchemy.orm import Session

from ..models import Suburb


def get_suburb_service(
    db: Session,
    limit: int = 100,
    larger_region: str | None = None,
) -> dict:
    keywords = {}
    if larger_region:
        keywords["sa3_name"] = larger_region

    query = db.query(Suburb).filter_by(**keywords).order_by(Suburb.name)
    rows = query.limit(limit).all()
    return {
        "suburbs": [
            {
                "locality": s.name,
                "postcode": s.postcode,
                "state": s.state,
                "long": s.lng,
                "lat": s.lat,
                "larger_region": s.sa3_name,
            }
            for s in rows
        ]
    }


def get_larger_regions_service(db: Session) -> dict:
    rows = (
        db.query(Suburb.sa3_name)
        .filter(Suburb.sa3_name.isnot(None))
        .distinct()
        .order_by(Suburb.sa3_name)
        .all()
    )
    return {"larger_regions": [row[0] for row in rows]}
