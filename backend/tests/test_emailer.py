from types import SimpleNamespace

from app.services import emailer


def test_email_client_uses_ssl_for_port_465(monkeypatch):
    calls = {"ssl": False, "starttls": False, "login": None}

    class FakeServer:
        def __init__(self, host, port, timeout):
            calls["ssl"] = True
            assert host == "mail.example.com"
            assert port == 465
            assert timeout == 30

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def starttls(self):
            calls["starttls"] = True

        def login(self, user, password):
            calls["login"] = (user, password)

        def send_message(self, message):
            assert message["From"] == "mail@example.com"
            assert message["To"] == "lead@example.com"

    settings = SimpleNamespace(
        smtp_host="mail.example.com",
        smtp_port=465,
        smtp_user="mail@example.com",
        smtp_password="secret",
        smtp_from_email="mail@example.com",
        smtp_use_tls=True,
    )
    monkeypatch.setattr(emailer, "get_settings", lambda: settings)
    monkeypatch.setattr(emailer.smtplib, "SMTP_SSL", FakeServer)

    EmailClient = emailer.EmailClient
    EmailClient().send_email("lead@example.com", "Hello", "Body")

    assert calls["ssl"] is True
    assert calls["starttls"] is False
    assert calls["login"] == ("mail@example.com", "secret")
