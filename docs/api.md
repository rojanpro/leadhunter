# API Documentation

Use `Authorization: Bearer <token>` for dashboard API endpoints.

## Login

`POST /api/auth/login`

```json
{"email":"admin@example.com","password":"secret"}
```

`POST /api/auth/google`

```json
{"credential":"google-identity-services-id-token"}
```

The Google account email must match `DASHBOARD_ADMIN_EMAIL`.

## Campaigns

Create campaign with `POST /api/campaigns`.

Important fields:

- `keywords`: comma-separated business search terms
- `daily_whatsapp_limit`
- `daily_email_limit`
- `message_delay_seconds`
- `auto_send_whatsapp`
- `auto_send_email`
- `active`

## Manual Jobs

- `POST /api/jobs/run-discovery`
- `POST /api/leads/{id}/send-whatsapp`
- `POST /api/leads/{id}/send-email`
- `GET /api/settings/evolution-health`

## Webhooks

`POST /api/webhooks/evolution?secret=...`

Accepts Evolution message/status payloads. Incoming opt-out text marks the lead and contact identity as do-not-contact.
