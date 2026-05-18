from app.db.session import SessionLocal
from app.models.entities import Lead

db = SessionLocal()
try:
    total_leads = db.query(Lead).count()
    print(f"Total leads in local database: {total_leads}")
    
    # Print the last 5 leads in the database safely
    leads = db.query(Lead).order_by(Lead.id.desc()).limit(5).all()
    print("\nLast 5 leads in database:")
    for lead in leads:
        safe_name = lead.business_name.encode('ascii', errors='replace').decode('ascii')
        print(f"- ID: {lead.id}, Name: {safe_name}, Phone: {lead.phone}, Website: {lead.website}, Status: {lead.website_status}")
finally:
    db.close()
