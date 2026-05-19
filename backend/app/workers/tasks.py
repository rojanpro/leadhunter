import asyncio
import logging
import time
from datetime import datetime, timezone, timedelta
from app.workers.celery_app import celery_app as _celery_app
from celery import shared_task
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.entities import (
    Campaign, Lead, Message, DoNotContact, JobLog, WebsiteStatus, ContactStatus, MessageChannel,
    MessageDirection, MessageStatus, utcnow,
)
from app.services.places import GooglePlacesClient
from app.services.website import classify_website
from app.services.phone import normalize_phone_number
from app.services.scoring import calculate_seo_score
from app.services.dedupe import find_duplicate, merge_better_data
from app.services.templates import render_template
from app.services.sheets import GoogleSheetsClient
from app.services.evolution import EvolutionClient
from app.services.emailer import EmailClient
from app.services.enrichment import enrich_email_from_website
from app.services.personalization import personalize_message

log = logging.getLogger(__name__)
settings = get_settings()


def run_async(coro):
    return asyncio.run(coro)


def with_job_log(db: Session, job_type: str, meta: dict | None = None) -> JobLog:
    job = JobLog(job_type=job_type, status="RUNNING", meta=meta or {})
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def finish_job(db: Session, job: JobLog, status: str, error: str | None = None) -> None:
    job.status = status
    job.error_message = error
    job.finished_at = utcnow()
    db.commit()


def save_lead_from_search_data(db: Session, campaign: Campaign, details: dict) -> int | None:
    location = details.get("geometry", {}).get("location", {})
    phone = details.get("international_phone_number") or details.get("formatted_phone_number") or details.get("phone")
    source = details.get("source")
    website = details.get("website") or (details.get("url") if source == "organic_web" else None)
    lead = Lead(
        campaign_id=campaign.id,
        place_id=details.get("place_id"),
        business_name=details.get("name", "Unknown business"),
        category=", ".join(details.get("types", [])[:3]) if isinstance(details.get("types"), list) else details.get("category"),
        address=details.get("formatted_address") or details.get("address"),
        city=campaign.city,
        country=campaign.country,
        phone=phone,
        phone_normalized=normalize_phone_number(phone, campaign.country),
        website=website,
        website_status=run_async(classify_website(website)),
        google_maps_url=details.get("url") if source != "organic_web" else None,
        rating=details.get("rating"),
        review_count=details.get("user_ratings_total") or details.get("review_count"),
        business_status=details.get("business_status"),
        latitude=location.get("lat"),
        longitude=location.get("lng"),
        raw_data=details,
    )
    score, reason = calculate_seo_score(lead)
    lead.seo_score = score
    lead.lead_reason = reason
    existing = find_duplicate(db, lead)
    if existing:
        merge_better_data(existing, lead)
        db.commit()
        return existing.id
    db.add(lead)
    db.commit()
    db.refresh(lead)
    enrich_email_for_lead.delay(lead.id)
    generate_messages_for_lead.delay(lead.id)
    sync_lead_to_google_sheet.delay(lead.id)
    if campaign.auto_send_whatsapp:
        send_whatsapp_for_lead.delay(lead.id)
    if campaign.auto_send_email:
        send_email_for_lead.delay(lead.id)
    return lead.id


@shared_task(name="app.workers.tasks.run_active_campaigns")
def run_active_campaigns() -> dict:
    db = SessionLocal()
    job = with_job_log(db, "run_active_campaigns")
    try:
        campaigns = db.query(Campaign).filter(Campaign.active.is_(True)).all()
        for campaign in campaigns:
            discover_leads_for_campaign.delay(campaign.id)
        finish_job(db, job, "SUCCESS", None)
        return {"queued_campaigns": len(campaigns)}
    except Exception as exc:
        log.exception("Active campaign run failed")
        finish_job(db, job, "FAILED", str(exc))
        raise
    finally:
        db.close()


@shared_task(bind=True, name="app.workers.tasks.discover_leads_for_campaign", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def discover_leads_for_campaign(self, campaign_id: int) -> dict:
    db = SessionLocal()
    job = with_job_log(db, "discover_leads_for_campaign", {"campaign_id": campaign_id})
    try:
        campaign = db.get(Campaign, campaign_id)
        if not campaign or not campaign.active:
            finish_job(db, job, "SKIPPED")
            return {"status": "skipped"}
        client = GooglePlacesClient()
        queries = [item.strip() for item in campaign.keywords.split(",") if item.strip()] or [campaign.business_type]
        location = ", ".join(part for part in [campaign.city.strip(), campaign.country.strip()] if part)
        queued = 0
        for keyword in queries:
            search_query = f"{keyword} in {location}" if location else keyword
            results = run_async(client.search(search_query, settings.max_places_per_run))
            for result in results:
                place_id = result.get("place_id")
                if place_id and result.get("source") not in {"organic_web", "openstreetmap"}:
                    process_place_details.delay(place_id, campaign.id)
                    queued += 1
                else:
                    process_search_result.delay(result, campaign.id)
                    queued += 1
        finish_job(db, job, "SUCCESS", None)
        return {"queued_leads": queued}
    except Exception as exc:
        finish_job(db, job, "FAILED", str(exc))
        raise
    finally:
        db.close()


@shared_task(bind=True, name="app.workers.tasks.process_place_details", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def process_place_details(self, place_id: str, campaign_id: int) -> int | None:
    db = SessionLocal()
    try:
        campaign = db.get(Campaign, campaign_id)
        if not campaign:
            return None
        details = run_async(GooglePlacesClient().details(place_id))
        if not details:
            return None
        details["place_id"] = details.get("place_id") or place_id
        return save_lead_from_search_data(db, campaign, details)
    finally:
        db.close()


@shared_task(bind=True, name="app.workers.tasks.process_search_result", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def process_search_result(self, result: dict, campaign_id: int) -> int | None:
    db = SessionLocal()
    try:
        campaign = db.get(Campaign, campaign_id)
        if not campaign:
            return None
        return save_lead_from_search_data(db, campaign, result)
    finally:
        db.close()


@shared_task(name="app.workers.tasks.qualify_and_score_lead")
def qualify_and_score_lead(lead_id: int) -> dict:
    db = SessionLocal()
    try:
        lead = db.get(Lead, lead_id)
        if not lead:
            return {"status": "missing"}
        score, reason = calculate_seo_score(lead)
        lead.seo_score = score
        lead.lead_reason = reason
        db.commit()
        return {"seo_score": score}
    finally:
        db.close()


@shared_task(name="app.workers.tasks.generate_messages_for_lead")
def generate_messages_for_lead(lead_id: int) -> dict:
    db = SessionLocal()
    try:
        lead = db.get(Lead, lead_id)
        if not lead:
            return {"status": "missing"}
        whatsapp_base = render_template(lead.campaign.whatsapp_template, lead, lead.campaign)
        email_base = render_template(lead.campaign.email_template, lead, lead.campaign)
        lead.whatsapp_message = run_async(personalize_message("whatsapp", whatsapp_base, lead, lead.campaign))
        lead.email_subject = render_template(lead.campaign.email_subject_template, lead, lead.campaign)
        lead.email_body = run_async(personalize_message("email", email_base, lead, lead.campaign))
        if lead.contact_status == ContactStatus.NEW:
            lead.contact_status = ContactStatus.MESSAGE_GENERATED
        db.commit()
        return {"status": "generated"}
    finally:
        db.close()


@shared_task(bind=True, name="app.workers.tasks.enrich_email_for_lead", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 2})
def enrich_email_for_lead(self, lead_id: int) -> dict:
    db = SessionLocal()
    try:
        lead = db.get(Lead, lead_id)
        if not lead:
            return {"status": "missing"}
        if lead.email:
            return {"status": "already_has_email"}
        email = run_async(enrich_email_from_website(lead.website))
        if not email:
            return {"status": "not_found"}
        blocked = db.query(DoNotContact).filter(DoNotContact.email == email).first()
        if blocked:
            return {"status": "blocked_email"}
        lead.email = email
        db.commit()
        sync_lead_to_google_sheet.delay(lead.id)
        if lead.campaign.auto_send_email:
            send_email_for_lead.delay(lead.id)
        return {"status": "enriched", "email": email}
    finally:
        db.close()


@shared_task(bind=True, name="app.workers.tasks.sync_lead_to_google_sheet", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def sync_lead_to_google_sheet(self, lead_id: int) -> dict:
    db = SessionLocal()
    try:
        lead = db.get(Lead, lead_id)
        if not lead:
            return {"status": "missing"}
        GoogleSheetsClient().append_lead(lead)
        return {"status": "synced"}
    finally:
        db.close()


@shared_task(bind=True, name="app.workers.tasks.check_whatsapp_for_lead", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def check_whatsapp_for_lead(self, lead_id: int) -> bool:
    db = SessionLocal()
    try:
        lead = db.get(Lead, lead_id)
        if not lead or not lead.phone_normalized:
            return False
        exists = run_async(EvolutionClient().check_whatsapp_number(lead.phone_normalized))
        lead.whatsapp_exists = exists
        if exists:
            lead.contact_status = ContactStatus.WHATSAPP_EXISTS
        db.commit()
        return exists
    finally:
        db.close()


def sent_today_count(db: Session, campaign_id: int, channel: MessageChannel) -> int:
    since = datetime.now(timezone.utc) - timedelta(days=1)
    return db.query(func.count(Message.id)).filter(
        Message.campaign_id == campaign_id,
        Message.channel == channel,
        Message.direction == MessageDirection.outbound,
        Message.status == MessageStatus.SENT,
        Message.sent_at >= since,
    ).scalar() or 0


def already_contacted(db: Session, lead: Lead, channel: MessageChannel) -> bool:
    return db.query(Message).filter(
        Message.lead_id == lead.id,
        Message.campaign_id == lead.campaign_id,
        Message.channel == channel,
        Message.direction == MessageDirection.outbound,
        Message.status.in_([MessageStatus.SENT, MessageStatus.DELIVERED]),
    ).first() is not None


def is_blocked(db: Session, lead: Lead) -> bool:
    return lead.do_not_contact or db.query(DoNotContact).filter(
        (DoNotContact.phone == lead.phone_normalized) | (DoNotContact.email == lead.email)
    ).first() is not None


@shared_task(bind=True, name="app.workers.tasks.send_whatsapp_for_lead", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_whatsapp_for_lead(self, lead_id: int) -> dict:
    db = SessionLocal()
    try:
        lead = db.get(Lead, lead_id)
        if not lead or not lead.phone_normalized:
            return {"status": "missing_phone"}
        if is_blocked(db, lead) or already_contacted(db, lead, MessageChannel.whatsapp):
            return {"status": "blocked_or_duplicate"}
        if sent_today_count(db, lead.campaign_id, MessageChannel.whatsapp) >= min(lead.campaign.daily_whatsapp_limit, settings.max_whatsapp_per_day):
            return {"status": "daily_limit_reached"}
        if not lead.whatsapp_message:
            generate_messages_for_lead(lead.id)
            db.refresh(lead)
        exists = lead.whatsapp_exists if lead.whatsapp_exists is not None else check_whatsapp_for_lead(lead.id)
        if not exists:
            return {"status": "not_on_whatsapp"}
        time.sleep(min(lead.campaign.message_delay_seconds, 600))
        provider_id = run_async(EvolutionClient().send_whatsapp_message(lead.phone_normalized, lead.whatsapp_message or ""))
        message = Message(
            lead_id=lead.id,
            campaign_id=lead.campaign_id,
            channel=MessageChannel.whatsapp,
            direction=MessageDirection.outbound,
            body=lead.whatsapp_message or "",
            status=MessageStatus.SENT,
            provider_message_id=provider_id,
            sent_at=utcnow(),
        )
        lead.contact_status = ContactStatus.WHATSAPP_SENT
        lead.last_contacted_at = utcnow()
        db.add(message)
        db.commit()
        sync_lead_to_google_sheet.delay(lead.id)
        return {"status": "sent", "provider_message_id": provider_id}
    except Exception as exc:
        if "lead" in locals() and lead:
            db.add(Message(lead_id=lead.id, campaign_id=lead.campaign_id, channel=MessageChannel.whatsapp, direction=MessageDirection.outbound, body=lead.whatsapp_message or "", status=MessageStatus.FAILED, error_message=str(exc)))
            db.commit()
        raise
    finally:
        db.close()


@shared_task(bind=True, name="app.workers.tasks.send_email_for_lead", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_email_for_lead(self, lead_id: int) -> dict:
    db = SessionLocal()
    try:
        lead = db.get(Lead, lead_id)
        if not lead or not lead.email:
            return {"status": "missing_email"}
        if is_blocked(db, lead) or already_contacted(db, lead, MessageChannel.email):
            return {"status": "blocked_or_duplicate"}
        if sent_today_count(db, lead.campaign_id, MessageChannel.email) >= min(lead.campaign.daily_email_limit, settings.max_email_per_day):
            return {"status": "daily_limit_reached"}
        if not lead.email_body:
            generate_messages_for_lead(lead.id)
            db.refresh(lead)
        provider_id = EmailClient().send_email(lead.email, lead.email_subject or "Quick idea", lead.email_body or "")
        message = Message(
            lead_id=lead.id,
            campaign_id=lead.campaign_id,
            channel=MessageChannel.email,
            direction=MessageDirection.outbound,
            subject=lead.email_subject,
            body=lead.email_body or "",
            status=MessageStatus.SENT,
            provider_message_id=provider_id,
            sent_at=utcnow(),
        )
        lead.contact_status = ContactStatus.EMAIL_SENT
        lead.last_contacted_at = utcnow()
        db.add(message)
        db.commit()
        sync_lead_to_google_sheet.delay(lead.id)
        return {"status": "sent"}
    finally:
        db.close()


@shared_task(name="app.workers.tasks.process_followups")
def process_followups() -> dict:
    return {"status": "no_followup_rules_configured"}


@shared_task(name="app.workers.tasks.handle_failed_jobs")
def handle_failed_jobs() -> dict:
    db = SessionLocal()
    try:
        failed = db.query(JobLog).filter(JobLog.status == "FAILED", JobLog.finished_at >= utcnow() - timedelta(days=1)).count()
        return {"failed_jobs_24h": failed}
    finally:
        db.close()
