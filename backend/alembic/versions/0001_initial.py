"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    website_status = postgresql.ENUM("NO_WEBSITE", "SOCIAL_ONLY", "HAS_WEBSITE", "BAD_WEBSITE", "UNKNOWN", name="websitestatus", create_type=False)
    contact_status = postgresql.ENUM("NEW", "MESSAGE_GENERATED", "WHATSAPP_EXISTS", "WHATSAPP_SENT", "WHATSAPP_REPLIED", "EMAIL_SENT", "REPLIED", "CONVERTED", "FAILED", "STOPPED", "DO_NOT_CONTACT", name="contactstatus", create_type=False)
    channel = postgresql.ENUM("whatsapp", "email", name="messagechannel", create_type=False)
    direction = postgresql.ENUM("outbound", "inbound", name="messagedirection", create_type=False)
    message_status = postgresql.ENUM("NEW", "GENERATED", "SENT", "DELIVERED", "FAILED", "BOUNCED", "REPLIED", "DO_NOT_CONTACT", name="messagestatus", create_type=False)
    website_status.create(op.get_bind(), checkfirst=True)
    contact_status.create(op.get_bind(), checkfirst=True)
    channel.create(op.get_bind(), checkfirst=True)
    direction.create(op.get_bind(), checkfirst=True)
    message_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("business_type", sa.String(255), nullable=False),
        sa.Column("city", sa.String(120), nullable=False),
        sa.Column("country", sa.String(120), nullable=False),
        sa.Column("keywords", sa.Text(), nullable=False),
        sa.Column("radius", sa.Integer(), nullable=False),
        sa.Column("offer", sa.Text(), nullable=False),
        sa.Column("your_name", sa.String(120), nullable=False),
        sa.Column("agency_name", sa.String(160), nullable=False),
        sa.Column("whatsapp_template", sa.Text(), nullable=False),
        sa.Column("email_subject_template", sa.Text(), nullable=False),
        sa.Column("email_template", sa.Text(), nullable=False),
        sa.Column("daily_whatsapp_limit", sa.Integer(), nullable=False),
        sa.Column("daily_email_limit", sa.Integer(), nullable=False),
        sa.Column("message_delay_seconds", sa.Integer(), nullable=False),
        sa.Column("auto_send_whatsapp", sa.Boolean(), nullable=False),
        sa.Column("auto_send_email", sa.Boolean(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "do_not_contact",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("phone", sa.String(80), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_do_not_contact_phone", "do_not_contact", ["phone"])
    op.create_index("ix_do_not_contact_email", "do_not_contact", ["email"])
    op.create_table(
        "job_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_type", sa.String(120), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
    )
    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("place_id", sa.String(255), nullable=True),
        sa.Column("business_name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(255), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(120), nullable=False),
        sa.Column("country", sa.String(120), nullable=False),
        sa.Column("phone", sa.String(80), nullable=True),
        sa.Column("phone_normalized", sa.String(80), nullable=True),
        sa.Column("whatsapp_exists", sa.Boolean(), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("website", sa.Text(), nullable=True),
        sa.Column("website_status", website_status, nullable=False),
        sa.Column("google_maps_url", sa.Text(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("business_status", sa.String(80), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("seo_score", sa.Integer(), nullable=False),
        sa.Column("lead_reason", sa.Text(), nullable=True),
        sa.Column("whatsapp_message", sa.Text(), nullable=True),
        sa.Column("email_subject", sa.Text(), nullable=True),
        sa.Column("email_body", sa.Text(), nullable=True),
        sa.Column("contact_status", contact_status, nullable=False),
        sa.Column("do_not_contact", sa.Boolean(), nullable=False),
        sa.Column("reply_message", sa.Text(), nullable=True),
        sa.Column("followup_count", sa.Integer(), nullable=False),
        sa.Column("last_contacted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_data", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("place_id", name="uq_leads_place_id"),
    )
    op.create_index("ix_leads_phone_normalized", "leads", ["phone_normalized"])
    op.create_index("ix_leads_email", "leads", ["email"])
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", channel, nullable=False),
        sa.Column("direction", direction, nullable=False),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", message_status, nullable=False),
        sa.Column("provider_message_id", sa.String(255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("messages")
    op.drop_index("ix_leads_email", table_name="leads")
    op.drop_index("ix_leads_phone_normalized", table_name="leads")
    op.drop_table("leads")
    op.drop_table("job_logs")
    op.drop_index("ix_do_not_contact_email", table_name="do_not_contact")
    op.drop_index("ix_do_not_contact_phone", table_name="do_not_contact")
    op.drop_table("do_not_contact")
    op.drop_table("campaigns")
    for enum_name in ["messagestatus", "messagedirection", "messagechannel", "contactstatus", "websitestatus"]:
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
