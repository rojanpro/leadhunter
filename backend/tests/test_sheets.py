from app.services.sheets import SHEET_HEADERS


def test_sheet_headers_include_required_columns():
    assert "lead_id" in SHEET_HEADERS
    assert "website_status" in SHEET_HEADERS
    assert "do_not_contact" in SHEET_HEADERS
