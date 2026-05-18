from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from app.models.entities import Lead


def find_duplicate(db: Session, lead: Lead) -> Lead | None:
    clauses = []
    if lead.place_id:
        clauses.append(Lead.place_id == lead.place_id)
    if lead.phone_normalized:
        clauses.append(Lead.phone_normalized == lead.phone_normalized)
    if lead.email:
        clauses.append(Lead.email == lead.email)
    if lead.business_name and lead.address:
        clauses.append(and_(Lead.business_name.ilike(lead.business_name), Lead.address.ilike(lead.address)))
    if not clauses:
        return None
    return db.query(Lead).filter(or_(*clauses)).first()


def merge_better_data(existing: Lead, incoming: Lead) -> Lead:
    for field in [
        "phone", "phone_normalized", "email", "website", "google_maps_url", "rating", "review_count",
        "business_status", "latitude", "longitude", "category", "address",
    ]:
        if getattr(incoming, field) and not getattr(existing, field):
            setattr(existing, field, getattr(incoming, field))
    if incoming.seo_score > existing.seo_score:
        existing.seo_score = incoming.seo_score
        existing.lead_reason = incoming.lead_reason
    return existing
