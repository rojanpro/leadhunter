from app.services.phone import normalize_phone_number


def test_normalize_nepal_phone():
    assert normalize_phone_number("984-123-4567", "Nepal") == "+9779841234567"


def test_invalid_phone_returns_none():
    assert normalize_phone_number("abc", "Nepal") is None
