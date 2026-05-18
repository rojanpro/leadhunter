import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException


COUNTRY_TO_REGION = {
    "nepal": "NP",
    "india": "IN",
    "united states": "US",
    "usa": "US",
    "united kingdom": "GB",
    "australia": "AU",
}


def normalize_phone_number(phone: str | None, country_code: str | None = None) -> str | None:
    if not phone:
        return None
    region = COUNTRY_TO_REGION.get((country_code or "").strip().lower(), country_code or None)
    cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    try:
        parsed = phonenumbers.parse(cleaned, region)
    except NumberParseException:
        return None
    if not phonenumbers.is_possible_number(parsed):
        return None
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
