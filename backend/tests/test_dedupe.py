from app.models.entities import Lead, WebsiteStatus
from app.services.dedupe import merge_better_data


def test_merge_better_data_updates_missing_values():
    existing = Lead(campaign_id=1, business_name="A", city="Kathmandu", country="Nepal", website_status=WebsiteStatus.NO_WEBSITE, seo_score=20)
    incoming = Lead(campaign_id=1, business_name="A", city="Kathmandu", country="Nepal", website_status=WebsiteStatus.NO_WEBSITE, phone_normalized="+9779841234567", seo_score=80, lead_reason="Better")
    merge_better_data(existing, incoming)
    assert existing.phone_normalized == "+9779841234567"
    assert existing.seo_score == 80
