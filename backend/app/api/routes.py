from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.config import Settings, get_settings
from app.core.security import create_access_token, get_current_user, verify_google_credential, verify_password
from app.db.session import get_db
from app.models.entities import Campaign, Lead, Message, DoNotContact, ContactStatus
from app.schemas.api import CampaignCreate, CampaignOut, CampaignUpdate, GoogleLoginRequest, LeadOut, MessageOut, LoginRequest, TokenOut
from app.services.webhooks import handle_evolution_webhook
from app.services.evolution import EvolutionClient
from app.workers.tasks import discover_leads_for_campaign, run_active_campaigns, send_email_for_lead, send_whatsapp_for_lead

router = APIRouter()


@router.post("/auth/login", response_model=TokenOut)
def login(payload: LoginRequest, settings: Settings = Depends(get_settings)) -> TokenOut:
    if payload.email != settings.dashboard_admin_email or not verify_password(payload.password, settings.dashboard_admin_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenOut(access_token=create_access_token(payload.email))


@router.post("/auth/google", response_model=TokenOut)
def google_login(payload: GoogleLoginRequest, settings: Settings = Depends(get_settings)) -> TokenOut:
    email = verify_google_credential(payload.credential, settings)
    return TokenOut(access_token=create_access_token(email))


@router.get("/overview")
def overview(db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    total = db.query(func.count(Lead.id)).scalar() or 0
    qualified = db.query(func.count(Lead.id)).filter(Lead.website_status.in_(["NO_WEBSITE", "SOCIAL_ONLY", "BAD_WEBSITE"])).scalar() or 0
    wa_sent = db.query(func.count(Message.id)).filter(Message.channel == "whatsapp", Message.status == "SENT").scalar() or 0
    email_sent = db.query(func.count(Message.id)).filter(Message.channel == "email", Message.status == "SENT").scalar() or 0
    replies = db.query(func.count(Message.id)).filter(Message.direction == "inbound").scalar() or 0
    failed = db.query(func.count(Message.id)).filter(Message.status == "FAILED").scalar() or 0
    return {"total_leads": total, "qualified_leads": qualified, "whatsapp_sent": wa_sent, "email_sent": email_sent, "replies": replies, "failed_messages": failed}


@router.get("/campaigns", response_model=list[CampaignOut])
def list_campaigns(db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    return db.query(Campaign).order_by(Campaign.created_at.desc()).all()


@router.post("/campaigns", response_model=CampaignOut)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    campaign = Campaign(**payload.model_dump())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("/campaigns/{campaign_id}", response_model=CampaignOut)
def get_campaign(campaign_id: int, db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    return campaign


@router.put("/campaigns/{campaign_id}", response_model=CampaignOut)
def update_campaign(campaign_id: int, payload: CampaignUpdate, db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(campaign, key, value)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.delete("/campaigns/{campaign_id}")
def delete_campaign(campaign_id: int, db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    db.delete(campaign)
    db.commit()
    return {"status": "deleted"}


@router.post("/campaigns/{campaign_id}/start")
def start_campaign(campaign_id: int, db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    campaign.active = True
    db.commit()
    discover_leads_for_campaign.delay(campaign_id)
    return {"status": "started"}


@router.post("/campaigns/{campaign_id}/pause")
def pause_campaign(campaign_id: int, db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    campaign.active = False
    db.commit()
    return {"status": "paused"}


@router.get("/leads", response_model=list[LeadOut])
def list_leads(campaign_id: int | None = None, website_status: str | None = None, do_not_contact: bool | None = None, db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    query = db.query(Lead)
    if campaign_id:
        query = query.filter(Lead.campaign_id == campaign_id)
    if website_status:
        query = query.filter(Lead.website_status == website_status)
    if do_not_contact is not None:
        query = query.filter(Lead.do_not_contact == do_not_contact)
    return query.order_by(Lead.created_at.desc()).limit(500).all()


@router.get("/leads/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int, db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    return lead


@router.post("/leads/{lead_id}/send-whatsapp")
def send_whatsapp(lead_id: int, _: str = Depends(get_current_user)):
    send_whatsapp_for_lead.delay(lead_id)
    return {"status": "queued"}


@router.post("/leads/{lead_id}/send-email")
def send_email(lead_id: int, _: str = Depends(get_current_user)):
    send_email_for_lead.delay(lead_id)
    return {"status": "queued"}


@router.post("/leads/{lead_id}/mark-do-not-contact")
def mark_dnc(lead_id: int, db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    lead.do_not_contact = True
    lead.contact_status = ContactStatus.DO_NOT_CONTACT
    db.add(DoNotContact(phone=lead.phone_normalized, email=lead.email, reason="manual"))
    db.commit()
    return {"status": "marked"}


@router.post("/leads/{lead_id}/mark-converted")
def mark_converted(lead_id: int, db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    lead.contact_status = ContactStatus.CONVERTED
    db.commit()
    return {"status": "converted"}


@router.get("/messages", response_model=list[MessageOut])
def list_messages(db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    return db.query(Message).order_by(Message.created_at.desc()).limit(500).all()


@router.post("/jobs/run-discovery")
def run_discovery(_: str = Depends(get_current_user)):
    run_active_campaigns.delay()
    return {"status": "queued"}


@router.post("/jobs/run-outreach")
def run_outreach(_: str = Depends(get_current_user)):
    return {"status": "manual outreach is available per lead"}


@router.post("/webhooks/evolution")
async def evolution_webhook(request: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    secret = request.headers.get("x-webhook-secret") or request.query_params.get("secret")
    if settings.evolution_webhook_secret and secret != settings.evolution_webhook_secret:
        raise HTTPException(401, "Invalid webhook secret")
    return handle_evolution_webhook(db, await request.json())


@router.post("/webhooks/gmail")
async def gmail_webhook(request: Request):
    return {"status": "accepted", "payload_size": len(await request.body())}


@router.get("/settings/status")
def settings_status(settings: Settings = Depends(get_settings), _: str = Depends(get_current_user)):
    return {
        "google_places": bool(settings.google_places_api_key),
        "organic_search": True,
        "google_login": bool(settings.google_oauth_client_id),
        "google_sheets": bool(settings.google_sheet_id and settings.google_sheets_credentials_json),
        "evolution": bool(settings.evolution_base_url and settings.evolution_api_key and settings.evolution_instance_name),
        "smtp": bool(settings.smtp_host and settings.smtp_user and settings.smtp_password),
        "openai": bool(settings.openai_api_key),
        "scheduler_minutes": settings.lead_search_interval_minutes,
    }


@router.get("/settings/evolution-health")
async def evolution_health(_: str = Depends(get_current_user)):
    return await EvolutionClient().health()
