import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from app.core.config import get_settings

settings = get_settings()

try:
    print("Reading Google Sheet values...")
    creds_info = json.loads(settings.google_sheets_credentials_json)
    creds = Credentials.from_service_account_info(creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    
    result = service.spreadsheets().values().get(
        spreadsheetId=settings.google_sheet_id,
        range="Leads!A1:Z100"
    ).execute()
    
    rows = result.get("values", [])
    print(f"Successfully connected! Found {len(rows)} rows in the 'Leads' sheet (including headers).")
    
    if len(rows) > 1:
        print("\nLast 5 rows in the Google Sheet:")
        for idx, row in enumerate(rows[-5:]):
            safe_row = [str(cell).encode('ascii', errors='replace').decode('ascii') for cell in row]
            # print safe name (business_name is column index 3)
            name = safe_row[3] if len(safe_row) > 3 else "Unknown"
            lead_id = safe_row[0] if len(safe_row) > 0 else "N/A"
            website = safe_row[12] if len(safe_row) > 12 else "N/A"
            print(f"- Row {len(rows) - len(rows[-5:]) + idx + 1} | Lead ID: {lead_id} | Name: {name} | Website: {website}")
    else:
        print("\nNo lead data rows found in the sheet yet.")
        
except Exception as e:
    print("Error reading Google Sheet:", e)
