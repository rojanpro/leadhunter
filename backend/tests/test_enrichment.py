from app.services.enrichment import extract_emails


def test_extract_emails_filters_and_dedupes():
    text = "Email info@clinic.com or INFO@clinic.com. Ignore test@example.com and image@asset.png"
    assert extract_emails(text) == ["info@clinic.com"]
