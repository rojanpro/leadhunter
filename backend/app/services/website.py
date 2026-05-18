from urllib.parse import urlparse
import httpx
from app.models.entities import WebsiteStatus

SOCIAL_DOMAINS = (
    "facebook.com",
    "instagram.com",
    "linktr.ee",
    "business.site",
    "wa.me",
    "whatsapp.com",
    "x.com",
    "twitter.com",
    "tiktok.com",
)


def is_social_only(url: str | None) -> bool:
    if not url:
        return False
    host = urlparse(url if "://" in url else f"https://{url}").netloc.lower()
    return any(domain in host for domain in SOCIAL_DOMAINS)


async def classify_website(url: str | None) -> WebsiteStatus:
    if not url:
        return WebsiteStatus.NO_WEBSITE
    if is_social_only(url):
        return WebsiteStatus.SOCIAL_ONLY
    normalized = url if url.startswith(("http://", "https://")) else f"https://{url}"
    try:
        async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
            response = await client.get(normalized)
        if response.status_code >= 400:
            return WebsiteStatus.BAD_WEBSITE
        if response.elapsed.total_seconds() > 5:
            return WebsiteStatus.BAD_WEBSITE
        if urlparse(str(response.url)).scheme != "https":
            return WebsiteStatus.BAD_WEBSITE
        return WebsiteStatus.HAS_WEBSITE
    except httpx.HTTPError:
        return WebsiteStatus.BAD_WEBSITE
    except Exception:
        return WebsiteStatus.UNKNOWN
