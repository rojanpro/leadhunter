import enum
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WebsiteStatus(str, enum.Enum):
    NO_WEBSITE = "NO_WEBSITE"
    SOCIAL_ONLY = "SOCIAL_ONLY"
    HAS_WEBSITE = "HAS_WEBSITE"
    BAD_WEBSITE = "BAD_WEBSITE"
    UNKNOWN = "UNKNOWN"


class ContactStatus(str, enum.Enum):
    NEW = "NEW"
    MESSAGE_GENERATED = "MESSAGE_GENERATED"
    WHATSAPP_EXISTS = "WHATSAPP_EXISTS"
    WHATSAPP_SENT = "WHATSAPP_SENT"
    WHATSAPP_REPLIED = "WHATSAPP_REPLIED"
    EMAIL_SENT = "EMAIL_SENT"
    REPLIED = "REPLIED"
    CONVERTED = "CONVERTED"
    FAILED = "FAILED"
    STOPPED = "STOPPED"
    DO_NOT_CONTACT = "DO_NOT_CONTACT"


class MessageChannel(str, enum.Enum):
    whatsapp = "whatsapp"
    email = "email"


class MessageDirection(str, enum.Enum):
    outbound = "outbound"
    inbound = "inbound"


class MessageStatus(str, enum.Enum):
    NEW = "NEW"
    GENERATED = "GENERATED"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    BOUNCED = "BOUNCED"
    REPLIED = "REPLIED"
    DO_NOT_CONTACT = "DO_NOT_CONTACT"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_type: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    country: Mapped[str] = mapped_column(String(120), nullable=False)
    keywords: Mapped[str] = mapped_column(Text, nullable=False)
    radius: Mapped[int] = mapped_column(Integer, default=5000)
    offer: Mapped[str] = mapped_column(Text, default="Website design and local SEO")
    your_name: Mapped[str] = mapped_column(String(120), default="Rojan Shrestha")
    agency_name: Mapped[str] = mapped_column(String(160), default="ROJAN.PRO")
    whatsapp_template: Mapped[str] = mapped_column(Text, nullable=False)
    email_subject_template: Mapped[str] = mapped_column(Text, default="Quick idea for {{business_name}}")
    email_template: Mapped[str] = mapped_column(Text, nullable=False)
    daily_whatsapp_limit: Mapped[int] = mapped_column(Integer, default=30)
    daily_email_limit: Mapped[int] = mapped_column(Integer, default=30)
    message_delay_seconds: Mapped[int] = mapped_column(Integer, default=90)
    auto_send_whatsapp: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_send_email: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    leads: Mapped[list["Lead"]] = relationship(back_populates="campaign")


class Lead(Base):
    __tablename__ = "leads"
    __table_args__ = (
        UniqueConstraint("place_id", name="uq_leads_place_id"),
        Index("ix_leads_phone_normalized", "phone_normalized"),
        Index("ix_leads_email", "email"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    place_id: Mapped[str | None] = mapped_column(String(255))
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    country: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(80))
    phone_normalized: Mapped[str | None] = mapped_column(String(80))
    whatsapp_exists: Mapped[bool | None] = mapped_column(Boolean)
    email: Mapped[str | None] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(Text)
    website_status: Mapped[WebsiteStatus] = mapped_column(Enum(WebsiteStatus), default=WebsiteStatus.UNKNOWN)
    google_maps_url: Mapped[str | None] = mapped_column(Text)
    rating: Mapped[float | None] = mapped_column(Float)
    review_count: Mapped[int | None] = mapped_column(Integer)
    business_status: Mapped[str | None] = mapped_column(String(80))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    seo_score: Mapped[int] = mapped_column(Integer, default=0)
    lead_reason: Mapped[str | None] = mapped_column(Text)
    whatsapp_message: Mapped[str | None] = mapped_column(Text)
    email_subject: Mapped[str | None] = mapped_column(Text)
    email_body: Mapped[str | None] = mapped_column(Text)
    contact_status: Mapped[ContactStatus] = mapped_column(Enum(ContactStatus), default=ContactStatus.NEW)
    do_not_contact: Mapped[bool] = mapped_column(Boolean, default=False)
    reply_message: Mapped[str | None] = mapped_column(Text)
    followup_count: Mapped[int] = mapped_column(Integer, default=0)
    last_contacted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    raw_data: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    campaign: Mapped[Campaign] = relationship(back_populates="leads")
    messages: Mapped[list["Message"]] = relationship(back_populates="lead")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    channel: Mapped[MessageChannel] = mapped_column(Enum(MessageChannel), nullable=False)
    direction: Mapped[MessageDirection] = mapped_column(Enum(MessageDirection), nullable=False)
    subject: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[MessageStatus] = mapped_column(Enum(MessageStatus), default=MessageStatus.NEW)
    provider_message_id: Mapped[str | None] = mapped_column(String(255))
    error_message: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    lead: Mapped[Lead] = relationship(back_populates="messages")


class DoNotContact(Base):
    __tablename__ = "do_not_contact"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone: Mapped[str | None] = mapped_column(String(80), index=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    reason: Mapped[str] = mapped_column(Text, default="opt-out")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class JobLog(Base):
    __tablename__ = "job_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_type: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    meta: Mapped[dict | None] = mapped_column("metadata", JSONB)
