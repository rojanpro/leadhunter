import logging
from typing import Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import get_settings

log = logging.getLogger(__name__)


class EvolutionClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def headers(self) -> dict[str, str]:
        return {"apikey": self.settings.evolution_api_key, "Content-Type": "application/json"}

    def configured(self) -> bool:
        return bool(self.settings.evolution_base_url and self.settings.evolution_api_key and self.settings.evolution_instance_name)

    async def health(self) -> dict[str, Any]:
        if not self.configured():
            return {"configured": False, "connected": False}
        url = f"{self.settings.evolution_base_url.rstrip('/')}/"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
        data: Any = response.json()
        return {
            "configured": True,
            "connected": response.status_code < 400,
            "version": data.get("version") if isinstance(data, dict) else None,
            "instance": self.settings.evolution_instance_name,
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=20), retry=retry_if_exception_type(httpx.HTTPError))
    async def check_whatsapp_number(self, phone: str) -> bool:
        if not self.configured():
            log.warning("Evolution API is not configured")
            return False
        url = f"{self.settings.evolution_base_url.rstrip('/')}/chat/whatsappNumbers/{self.settings.evolution_instance_name}"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(url, headers=self.headers, json={"numbers": [phone]})
            response.raise_for_status()
        data: Any = response.json()
        rows = data if isinstance(data, list) else data.get("numbers", data.get("data", []))
        if not rows:
            return False
        first = rows[0]
        return bool(first.get("exists") or first.get("jid") or first.get("numberExists"))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=20), retry=retry_if_exception_type(httpx.HTTPError))
    async def send_whatsapp_message(self, phone: str, message: str) -> str | None:
        if not self.configured():
            raise RuntimeError("Evolution API is not configured")
        url = f"{self.settings.evolution_base_url.rstrip('/')}/message/sendText/{self.settings.evolution_instance_name}"
        payload = {"number": phone, "text": message}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
        data = response.json()
        return data.get("key", {}).get("id") or data.get("messageId") or data.get("id")

    async def set_webhook(self, webhook_url: str) -> bool:
        if not self.configured():
            return False
        url = f"{self.settings.evolution_base_url.rstrip('/')}/webhook/set/{self.settings.evolution_instance_name}"
        payload = {"webhook": {"enabled": True, "url": webhook_url, "events": ["MESSAGES_UPSERT", "MESSAGES_UPDATE"]}}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
        return True
