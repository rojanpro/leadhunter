from app.models.entities import Campaign, Lead, WebsiteStatus
from app.services.templates import render_template


def test_template_rendering():
    campaign = Campaign(name="Dental", business_type="Dentist", city="Kathmandu", country="Nepal", keywords="dentist", whatsapp_template="Hi {{business_name}} in {{city}}", email_template="Body")
    lead = Lead(campaign_id=1, business_name="Smile Care", city="Kathmandu", country="Nepal", website_status=WebsiteStatus.NO_WEBSITE)
    assert render_template("Hi {{business_name}} in {{city}}", lead, campaign) == "Hi Smile Care in Kathmandu"
