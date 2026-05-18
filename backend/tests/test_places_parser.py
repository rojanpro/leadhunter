from app.services.phone import normalize_phone_number
from app.services.places import DuckDuckGoResultParser, clean_duckduckgo_url, is_usable_business_url, location_from_query, organic_place_id, osm_tags_for_query


def test_google_place_detail_fields_can_be_mapped():
    details = {
        "place_id": "abc",
        "name": "Smile Dental",
        "formatted_address": "Kathmandu",
        "international_phone_number": "+977 984-1234567",
        "types": ["dentist", "health"],
    }
    assert details["name"] == "Smile Dental"
    assert normalize_phone_number(details["international_phone_number"], "Nepal") == "+9779841234567"


def test_duckduckgo_redirect_url_is_cleaned():
    url = "https://duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fclinic"
    assert clean_duckduckgo_url(url) == "https://example.com/clinic"


def test_organic_result_parser_filters_directories():
    parser = DuckDuckGoResultParser()
    parser.feed("""
      <a class="result__a" href="https://duckduckgo.com/l/?uddg=https%3A%2F%2Fexampleclinic.com">Example Clinic</a>
      <a class="result__a" href="https://tripadvisor.com/example">Top clinics</a>
    """)
    assert parser.results == [{"title": "Example Clinic", "url": "https://exampleclinic.com"}]


def test_organic_place_id_is_stable():
    assert organic_place_id("https://exampleclinic.com/about") == "organic:exampleclinic.com/about"
    assert not is_usable_business_url("https://google.com/search?q=clinic")


def test_osm_query_helpers():
    assert location_from_query("dentist in Kathmandu, Nepal") == "Kathmandu, Nepal"
    assert ("amenity", "dentist") in osm_tags_for_query("dental clinic in Kathmandu")
    assert ("shop", "hairdresser") in osm_tags_for_query("barber in New York")
