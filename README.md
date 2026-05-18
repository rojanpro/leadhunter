# Autonomous AI Lead Hunter

Production-grade local business lead discovery and outreach system.

It searches for local businesses by campaign keywords and country, qualifies leads without a useful website, optionally enriches public emails from business websites, scores SEO opportunity, deduplicates contacts, syncs to Google Sheets, and sends controlled outreach through WhatsApp Evolution API and SMTP email. Google Places is optional; when no Places key is set, discovery falls back to organic web search.

## Stack

- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL
- Workers: Celery, Redis, Celery Beat scheduler
- Frontend: Next.js 15, Tailwind CSS, shadcn-style components
- Integrations: optional Google Places API, optional Gmail/Google dashboard login, Google Sheets API, Evolution API, SMTP, optional OpenAI key slot
- Deployment: Docker Compose, Nginx reverse proxy

## Quick Start

```powershell
Copy-Item .env.example .env
notepad .env
docker compose up --build
```

Open:

- Dashboard: `http://localhost:3000`
- Reverse proxy: `http://localhost:8080`
- Backend health: `http://localhost:8001/health`

The backend runs migrations and seeds a sample `Kathmandu Dental Clinics` campaign on startup.

## Safety Controls

- JWT-protected dashboard APIs
- Rate-limited FastAPI endpoints
- Do-not-contact database
- STOP/unsubscribe webhook handling
- Duplicate prevention by `place_id`, phone, email, and business/address
- Campaign daily WhatsApp and email limits
- Per-campaign message delay
- Optional OpenAI message personalization with template fallback
- Optional public email enrichment from business website/contact pages
- Celery retries with exponential backoff
- Secrets loaded from `.env`

## Required Environment

Copy `.env.example` to `.env` and set:

- `APP_SECRET_KEY`
- `DASHBOARD_ADMIN_EMAIL`
- `DASHBOARD_ADMIN_PASSWORD`
- `GOOGLE_OAUTH_CLIENT_ID` and `NEXT_PUBLIC_GOOGLE_CLIENT_ID` for Gmail login, optional
- `GOOGLE_PLACES_API_KEY`, optional
- `GOOGLE_SHEETS_CREDENTIALS_JSON`
- `GOOGLE_SHEET_ID`
- `EVOLUTION_BASE_URL`
- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE_NAME`
- `EVOLUTION_WEBHOOK_SECRET`
- SMTP settings

Auto sending is controlled per campaign. Keep `auto_send_whatsapp=false` and `auto_send_email=false` until you verify credentials, templates, legal compliance, and opt-out flow.

## Worker Commands

```bash
celery -A app.workers.celery_app.celery_app worker --loglevel=INFO
celery -A app.workers.celery_app.celery_app beat --loglevel=INFO
```

## API

Core endpoints:

- `GET /health`
- `POST /api/auth/login`
- `GET/POST /api/campaigns`
- `GET/PUT/DELETE /api/campaigns/{id}`
- `POST /api/campaigns/{id}/start`
- `POST /api/campaigns/{id}/pause`
- `GET /api/leads`
- `POST /api/leads/{id}/send-whatsapp`
- `POST /api/leads/{id}/send-email`
- `POST /api/leads/{id}/mark-do-not-contact`
- `POST /api/jobs/run-discovery`
- `POST /api/webhooks/evolution`
- `GET /api/settings/status`

Interactive OpenAPI docs are available at `http://localhost:8001/docs`.

## Google Sheet

Create a sheet tab named `Leads` and use the headers in `scripts/sheet_headers.csv`.

The system appends lead rows after discovery and after contact status changes.

## Compliance Note

This system enforces opt-out and duplicate prevention, but outreach laws vary by country and industry. Configure campaigns and limits to comply with the markets you target.
