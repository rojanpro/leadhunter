import logging
import re
from urllib.parse import urljoin
import httpx

log = logging.getLogger(__name__)

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
SKIP_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf")


def clean_email(email: str) -> str | None:
    value = email.strip().strip(".,;:()[]{}<>").lower()
    if value.endswith(SKIP_EXTENSIONS):
        return None
    if any(token in value for token in ["example.com", "domain.com", "sentry.io"]):
        return None
    return value


def extract_emails(text: str) -> list[str]:
    found: list[str] = []
    for match in EMAIL_RE.findall(text or ""):
        email = clean_email(match)
        if email and email not in found:
            found.append(email)
    return found


async def enrich_email_from_website(website: str | None) -> str | None:
    if not website:
        return None
    base_url = website if website.startswith(("http://", "https://")) else f"https://{website}"
    candidate_urls = [
        base_url,
        urljoin(base_url.rstrip("/") + "/", "contact"),
        urljoin(base_url.rstrip("/") + "/", "contact-us"),
        urljoin(base_url.rstrip("/") + "/", "about"),
    ]
    async with httpx.AsyncClient(timeout=10, follow_redirects=True, headers={"User-Agent": "LeadHunterBot/1.0"}) as client:
        for url in candidate_urls:
            try:
                response = await client.get(url)
                if response.status_code >= 400 or "text/html" not in response.headers.get("content-type", ""):
                    continue
                emails = extract_emails(response.text)
                if emails:
                    return emails[0]
            except httpx.HTTPError as exc:
                log.info("Email enrichment failed for %s: %s", url, exc)
    return None
