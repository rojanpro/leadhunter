from app.services.website import is_social_only


def test_social_only_detection():
    assert is_social_only("https://facebook.com/example")
    assert is_social_only("https://example.business.site")
    assert not is_social_only("https://exampleclinic.com")
