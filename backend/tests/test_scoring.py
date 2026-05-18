from app.models.entities import Lead, WebsiteStatus
from app.services.scoring import calculate_seo_score


def test_scoring_no_website_active_phone_reviews():
    lead = Lead(campaign_id=1, business_name="Clinic", city="Kathmandu", country="Nepal", phone_normalized="+9779841234567", website_status=WebsiteStatus.NO_WEBSITE, rating=4.5, review_count=42, business_status="OPERATIONAL", category="dental clinic")
    score, reason = calculate_seo_score(lead)
    assert score == 100
    assert "no website" in reason.lower()
