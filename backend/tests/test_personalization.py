import pytest
from app.models.entities import Campaign, Lead, WebsiteStatus
from app.services.personalization import personalize_message


@pytest.mark.asyncio
async def test_personalization_falls_back_without_openai_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    campaign = Campaign(name="Dental", business_type="Dentist", city="Kathmandu", country="Nepal", keywords="dentist", whatsapp_template="Hi", email_template="Body")
    lead = Lead(campaign_id=1, business_name="Smile Care", city="Kathmandu", country="Nepal", website_status=WebsiteStatus.NO_WEBSITE)
    assert await personalize_message("whatsapp", "Hi Smile Care", lead, campaign) == "Hi Smile Care"
