from sqlalchemy.orm import Session

from ..models import Suburb


def get_suburb_service(db: Session) -> dict:
    rows = db.query(Suburb).order_by(Suburb.name).all()
    return {
        "suburbs": [
            {
                "locality": s.name,
                "postcode": s.postcode,
                "state": s.state,
                "long": s.lng,
                "lat": s.lat,
                "larger_region": s.sa4_name,
            }
            for s in rows
        ]
    }
