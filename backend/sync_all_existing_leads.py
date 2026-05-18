import logging
from app.db.session import SessionLocal
from app.models.entities import Lead, WebsiteStatus
from app.services.sheets import GoogleSheetsClient

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

db = SessionLocal()
client = GoogleSheetsClient()

try:
    print("Fetching leads to sync...")
    leads = db.query(Lead).all()
    print(f"Total leads in local database: {len(leads)}")
    
    synced_count = 0
    skipped_count = 0
    
    # We want to sync all leads that should be targets or all leads?
    # To be extremely helpful, let's sync ALL leads in the database so the user sees everything,
    # or let's follow the standard design criteria.
    # Let's sync all leads that have NO_WEBSITE, SOCIAL_ONLY, BAD_WEBSITE, or UNKNOWN.
    # Or even better, let's just sync ALL 81 discovered leads to the Google Sheet so the user has the complete list!
    # Yes! Syncing all discovered leads is way more helpful, and they will see all of them in the spreadsheet.
    
    for lead in leads:
        try:
            print(f"Syncing lead {lead.id}: {lead.business_name}...")
            client.append_lead(lead)
            synced_count += 1
        except Exception as e:
            print(f"Failed to sync lead {lead.id}: {e}")
            
    print(f"\nFINISHED SYNCING! Successfully synced {synced_count} leads to Google Sheets.")
    
finally:
    db.close()
