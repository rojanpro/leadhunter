from jinja2 import Environment, BaseLoader, select_autoescape
from app.models.entities import Lead, Campaign

env = Environment(loader=BaseLoader(), autoescape=select_autoescape(default=False))


def render_template(template: str, lead: Lead, campaign: Campaign) -> str:
    data = {
        "business_name": lead.business_name,
        "category": lead.category or campaign.business_type,
        "city": lead.city,
        "country": lead.country,
        "website_status": lead.website_status.value,
        "lead_reason": lead.lead_reason or "",
        "your_name": campaign.your_name,
        "agency_name": campaign.agency_name,
        "offer": campaign.offer,
        "unsubscribe_text": "Reply STOP if you do not want messages.",
    }
    return env.from_string(template).render(**data).strip()
