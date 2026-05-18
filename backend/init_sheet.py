import sys
import os

# Add parent directory to sys.path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.sheets import GoogleSheetsClient

def init_sheet():
    print("Initializing Google Sheets client...")
    client = GoogleSheetsClient()
    if not client.configured():
        print("ERROR: Google Sheets is not fully configured in your backend/.env file!")
        print(f"GOOGLE_SHEET_ID: {'Set' if client.settings.google_sheet_id else 'Missing'}")
        print(f"GOOGLE_SHEETS_CREDENTIALS_JSON: {'Set' if client.settings.google_sheets_credentials_json else 'Missing'}")
        sys.exit(1)
    
    print(f"Connecting to Google Sheet with ID: {client.settings.google_sheet_id}")
    try:
        client.ensure_headers()
        print("SUCCESS: Google Sheet 'Leads' tab and headers have been successfully initialized/verified!")
    except Exception as e:
        print(f"ERROR: Failed to connect or initialize Google Sheet: {e}")
        print("\nPlease make sure that:")
        print("1. The Google Sheet ID is correct.")
        print("2. The Google Sheet has been SHARED with the client email of your service account:")
        try:
            import json
            creds = json.loads(client.settings.google_sheets_credentials_json)
            print(f"   => Shared with email: {creds.get('client_email')}")
        except Exception:
            pass
        sys.exit(1)

if __name__ == "__main__":
    init_sheet()
