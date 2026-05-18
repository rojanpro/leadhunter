# Deployment Guide

## Single Server Docker Deployment

1. Install Docker and Docker Compose.
2. Copy the repo to the server.
3. Create `.env` from `.env.example`.
4. Set production secrets and external API credentials.
5. Run:

```bash
docker compose up -d --build
```

## Services

- `backend`: FastAPI app, migrations, seed
- `worker`: Celery background jobs
- `scheduler`: Celery Beat every `LEAD_SEARCH_INTERVAL_MINUTES`
- `frontend`: Next.js dashboard
- `postgres`: persistent database volume
- `redis`: queue and task backend
- `nginx`: reverse proxy

## Production Hardening

- Put Nginx behind TLS.
- Set a long random `APP_SECRET_KEY`.
- Use a strong dashboard password or configure Gmail login with `GOOGLE_OAUTH_CLIENT_ID`.
- Restrict Google Places API key if you choose to use Places.
- Rotate Evolution and SMTP credentials regularly.
- Back up PostgreSQL.
- Monitor worker logs and failed `job_logs`.
