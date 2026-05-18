import logging
import httpx
from app.core.config import get_settings
from app.models.entities import Lead, Campaign

log = logging.getLogger(__name__)


async def personalize_message(channel: str, base_message: str, lead: Lead, campaign: Campaign) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        return base_message
    system = (
        "You improve short B2B outreach messages for local businesses. "
        "Keep meaning, keep opt-out text, avoid hype, avoid spammy wording, and return only the final message."
    )
    prompt = f"""
Channel: {channel}
Business: {lead.business_name}
Category: {lead.category or campaign.business_type}
City: {lead.city}
Website status: {lead.website_status.value}
Lead reason: {lead.lead_reason or ""}
Offer: {campaign.offer}

Base message:
{base_message}
""".strip()
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type": "application/json"},
                json={
                    "model": settings.openai_model,
                    "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                    "temperature": 0.4,
                    "max_tokens": 500,
                },
            )
            response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()
        return content or base_message
    except Exception as exc:
        log.warning("OpenAI personalization failed, using template fallback: %s", exc)
        return base_message
