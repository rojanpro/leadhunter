import json
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from app.core.config import get_settings
from app.models.entities import Lead

log = logging.getLogger(__name__)

SHEET_HEADERS = [
    "lead_id", "campaign_id", "campaign_name", "business_name", "category", "city", "country", "address",
    "phone", "phone_normalized", "whatsapp_exists", "email", "website", "website_status", "google_maps_url",
    "rating", "review_count", "seo_score", "lead_reason", "whatsapp_message", "whatsapp_status",
    "email_subject", "email_body", "email_status", "contact_status", "reply_message", "followup_count",
    "do_not_contact", "last_contacted_at", "created_at", "updated_at",
]


class GoogleSheetsClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def configured(self) -> bool:
        return bool(self.settings.google_sheet_id and self.settings.google_sheets_credentials_json)

    def _service(self):
        creds_info = json.loads(self.settings.google_sheets_credentials_json)
        creds = Credentials.from_service_account_info(creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        return build("sheets", "v4", credentials=creds, cache_discovery=False)

    def ensure_leads_sheet(self, service) -> None:
        spreadsheet = service.spreadsheets().get(spreadsheetId=self.settings.google_sheet_id).execute()
        sheets = spreadsheet.get("sheets", [])
        if any(sheet.get("properties", {}).get("title") == "Leads" for sheet in sheets):
            return
        service.spreadsheets().batchUpdate(
            spreadsheetId=self.settings.google_sheet_id,
            body={"requests": [{"addSheet": {"properties": {"title": "Leads"}}}]},
        ).execute()

    def ensure_headers(self) -> None:
        if not self.configured():
            log.warning("Google Sheets is not configured")
            return
        service = self._service()
        self.ensure_leads_sheet(service)
        service.spreadsheets().values().update(
            spreadsheetId=self.settings.google_sheet_id,
            range="Leads!A1:AE1",
            valueInputOption="RAW",
            body={"values": [SHEET_HEADERS]},
        ).execute()

    def append_lead(self, lead: Lead) -> None:
        if not self.configured():
            return
        row = [
            lead.id, lead.campaign_id, lead.campaign.name, lead.business_name, lead.category, lead.city, lead.country,
            lead.address, lead.phone, lead.phone_normalized, lead.whatsapp_exists, lead.email, lead.website,
            lead.website_status.value, lead.google_maps_url, lead.rating, lead.review_count, lead.seo_score,
            lead.lead_reason, lead.whatsapp_message, latest_status(lead, "whatsapp"), lead.email_subject,
            lead.email_body, latest_status(lead, "email"), lead.contact_status.value, lead.reply_message,
            lead.followup_count, lead.do_not_contact, str(lead.last_contacted_at or ""), str(lead.created_at), str(lead.updated_at),
        ]
        service = self._service()
        self.ensure_leads_sheet(service)
        service.spreadsheets().values().append(
            spreadsheetId=self.settings.google_sheet_id,
            range="Leads!A:AE",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]},
        ).execute()


def latest_status(lead: Lead, channel: str) -> str:
    for message in sorted(lead.messages, key=lambda item: item.created_at, reverse=True):
        if message.channel.value == channel:
            return message.status.value
    return "NEW"
