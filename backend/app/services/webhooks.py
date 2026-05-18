from sqlalchemy.orm import Session
from app.models.entities import Lead, Message, DoNotContact, ContactStatus, MessageChannel, MessageDirection, MessageStatus, utcnow
from app.services.optout import is_opt_out
from app.services.phone import normalize_phone_number


def extract_evolution_message(payload: dict) -> tuple[str | None, str | None, str | None, str | None]:
    data = payload.get("data", payload)
    key = data.get("key", {})
    remote = key.get("remoteJid") or data.get("remoteJid") or data.get("from")
    provider_id = key.get("id") or data.get("id")
    text = data.get("message", {}).get("conversation") or data.get("text") or data.get("body")
    status = data.get("status") or payload.get("event")
    phone = remote.split("@")[0] if isinstance(remote, str) else None
    return phone, text, provider_id, status


def handle_evolution_webhook(db: Session, payload: dict) -> dict:
    phone, text, provider_id, status = extract_evolution_message(payload)
    normalized = normalize_phone_number(phone, None) or phone
    lead = db.query(Lead).filter(Lead.phone_normalized == normalized).order_by(Lead.created_at.desc()).first()
    if not lead:
        return {"status": "ignored", "reason": "lead_not_found"}
    if text:
        message_status = MessageStatus.DO_NOT_CONTACT if is_opt_out(text) else MessageStatus.REPLIED
        message = Message(
            lead_id=lead.id,
            campaign_id=lead.campaign_id,
            channel=MessageChannel.whatsapp,
            direction=MessageDirection.inbound,
            body=text,
            status=message_status,
            provider_message_id=provider_id,
            replied_at=utcnow(),
        )
        lead.reply_message = text
        if is_opt_out(text):
            lead.do_not_contact = True
            lead.contact_status = ContactStatus.DO_NOT_CONTACT
            db.add(DoNotContact(phone=lead.phone_normalized, email=lead.email, reason=text[:500]))
        else:
            lead.contact_status = ContactStatus.WHATSAPP_REPLIED
        db.add(message)
        db.commit()
        return {"status": "processed", "lead_id": lead.id}
    if status and provider_id:
        message = db.query(Message).filter(Message.provider_message_id == provider_id).first()
        if message and "DELIVER" in status.upper():
            message.status = MessageStatus.DELIVERED
            message.delivered_at = utcnow()
        elif message and "FAIL" in status.upper():
            message.status = MessageStatus.FAILED
        db.commit()
    return {"status": "processed_status"}
