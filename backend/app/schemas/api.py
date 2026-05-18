from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class CampaignBase(BaseModel):
    name: str
    business_type: str
    city: str
    country: str
    keywords: str
    radius: int = 5000
    offer: str = "Website design and local SEO"
    your_name: str = "Your Name"
    agency_name: str = "Your Agency"
    whatsapp_template: str
    email_subject_template: str = "Quick idea for {{business_name}}"
    email_template: str
    daily_whatsapp_limit: int = 30
    daily_email_limit: int = 30
    message_delay_seconds: int = 90
    auto_send_whatsapp: bool = False
    auto_send_email: bool = False
    active: bool = True


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: str | None = None
    business_type: str | None = None
    city: str | None = None
    country: str | None = None
    keywords: str | None = None
    radius: int | None = None
    offer: str | None = None
    your_name: str | None = None
    agency_name: str | None = None
    whatsapp_template: str | None = None
    email_subject_template: str | None = None
    email_template: str | None = None
    daily_whatsapp_limit: int | None = None
    daily_email_limit: int | None = None
    message_delay_seconds: int | None = None
    auto_send_whatsapp: bool | None = None
    auto_send_email: bool | None = None
    active: bool | None = None


class CampaignOut(CampaignBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    campaign_id: int
    place_id: str | None
    business_name: str
    category: str | None
    address: str | None
    city: str
    country: str
    phone: str | None
    phone_normalized: str | None
    whatsapp_exists: bool | None
    email: EmailStr | None = None
    website: str | None
    website_status: str
    google_maps_url: str | None
    rating: float | None
    review_count: int | None
    seo_score: int
    lead_reason: str | None
    whatsapp_message: str | None
    email_subject: str | None
    email_body: str | None
    contact_status: str
    reply_message: str | None
    followup_count: int
    do_not_contact: bool
    last_contacted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    lead_id: int
    campaign_id: int
    channel: str
    direction: str
    subject: str | None
    body: str
    status: str
    provider_message_id: str | None
    error_message: str | None
    sent_at: datetime | None
    delivered_at: datetime | None
    replied_at: datetime | None
    created_at: datetime


class LoginRequest(BaseModel):
    email: str
    password: str


class GoogleLoginRequest(BaseModel):
    credential: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
