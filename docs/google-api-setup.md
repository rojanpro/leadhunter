# Google API Setup

Google Places is optional. If `GOOGLE_PLACES_API_KEY` is blank, lead discovery uses organic web search from the campaign keywords, city, and country.

For Gmail dashboard login:

1. Create or select a Google Cloud project.
2. Configure the OAuth consent screen.
3. Create an OAuth 2.0 Client ID for a web application.
4. Add your dashboard origin, for example `http://localhost:3000`, to authorized JavaScript origins.
5. Put the client ID in `.env` as both `GOOGLE_OAUTH_CLIENT_ID` and `NEXT_PUBLIC_GOOGLE_CLIENT_ID`.
6. Set `DASHBOARD_ADMIN_EMAIL` to the Gmail address allowed to sign in.

For optional Google Places:

1. Enable Places API.
2. Create an API key and restrict it to Places API.
3. Put the key in `.env` as `GOOGLE_PLACES_API_KEY`.

For Google Sheets:

1. Enable Google Sheets API.
2. Create a service account.
3. Generate a JSON key.
4. Share your Google Sheet with the service account email.
5. Paste the compact JSON into `GOOGLE_SHEETS_CREDENTIALS_JSON`.
6. Set `GOOGLE_SHEET_ID` from the sheet URL.
7. Create a tab named `Leads`.
8. Add headers from `scripts/sheet_headers.csv`.
