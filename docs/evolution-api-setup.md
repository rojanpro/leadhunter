# Evolution API Setup

Set these variables:

```env
EVOLUTION_BASE_URL=https://your-evolution-server.example.com
EVOLUTION_API_KEY=your-api-key
EVOLUTION_INSTANCE_NAME=your-instance
EVOLUTION_WEBHOOK_SECRET=your-random-webhook-secret
```

The backend uses:

- `GET /`
- `POST /chat/whatsappNumbers/{instanceName}`
- `POST /message/sendText/{instanceName}`
- `POST /webhook/set/{instanceName}`

The dashboard backend also exposes:

- `GET /api/settings/evolution-health`

Configure Evolution to post replies/statuses to:

```text
https://your-domain.com/api/webhooks/evolution?secret=EVOLUTION_WEBHOOK_SECRET
```

Incoming STOP/unsubscribe messages mark the lead as `DO_NOT_CONTACT` and block future WhatsApp/email outreach.
