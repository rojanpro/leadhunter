import sys
import os

# Ensure the backend directory is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.entities import Lead, Message, MessageChannel
from app.workers.tasks import send_email_for_lead

def main():
    db = SessionLocal()
    try:
        # Find all leads that have an email
        leads = db.query(Lead).filter(Lead.email.isnot(None)).all()
        
        # Find lead IDs that already have an outbound email sent
        sent_lead_ids = {
            m.lead_id for m in db.query(Message)
            .filter(Message.channel == MessageChannel.email)
            .all()
        }
        
        # Filter leads to only those that haven't been emailed
        pending = [l for l in leads if l.id not in sent_lead_ids]
        
        print(f"Total leads with email: {len(leads)}")
        print(f"Pending leads to email: {len(pending)}")
        
        for lead in pending:
            print(f"Queuing email for lead ID {lead.id} ({lead.email})...")
            send_email_for_lead.delay(lead.id)
            
        print("Done! The background workers will process the emails shortly.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
