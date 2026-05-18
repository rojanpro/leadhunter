from app.db.session import SessionLocal
from app.models.entities import Campaign

WHATSAPP_TEMPLATE = """Hi {{business_name}}, I found your business on Google Maps while searching for {{category}} in {{city}}.

I noticed you may not have a proper website yet. We help local businesses create modern websites and improve Google SEO so more customers can find and contact them online.

Would you like me to send a simple example for {{business_name}}?

Reply STOP if you do not want messages."""

EMAIL_TEMPLATE = """Hi {{business_name}},

I found your business on Google Maps while searching for {{category}} in {{city}}. I noticed you may not have a proper website yet.

We help local businesses build modern websites and improve Google visibility so more customers can find and contact them online.

Would you like me to send a simple example of how your website could look?

Regards,
{{your_name}}
{{agency_name}}

Reply unsubscribe if you do not want further messages."""


def seed() -> None:
    db = SessionLocal()
    try:
        exists = db.query(Campaign).filter(Campaign.name == "Kathmandu Dental Clinics").first()
        if exists:
            return
        db.add(Campaign(
            name="Kathmandu Dental Clinics",
            business_type="Dental clinics",
            city="Kathmandu",
            country="Nepal",
            keywords="dental clinic,dentist,dental care",
            radius=8000,
            offer="Website design and local SEO for dental clinics",
            your_name="Your Name",
            agency_name="Your Agency",
            whatsapp_template=WHATSAPP_TEMPLATE,
            email_subject_template="Quick idea for {{business_name}}",
            email_template=EMAIL_TEMPLATE,
            daily_whatsapp_limit=30,
            daily_email_limit=30,
            message_delay_seconds=90,
            auto_send_whatsapp=False,
            auto_send_email=False,
            active=True,
        ))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
