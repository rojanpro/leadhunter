from app.services.optout import is_opt_out
from app.services.webhooks import extract_evolution_message


def test_extract_evolution_message_and_stop():
    payload = {"data": {"key": {"remoteJid": "9779841234567@s.whatsapp.net", "id": "m1"}, "message": {"conversation": "STOP"}}}
    phone, text, provider_id, status = extract_evolution_message(payload)
    assert phone == "9779841234567"
    assert provider_id == "m1"
    assert status is None
    assert is_opt_out(text)
