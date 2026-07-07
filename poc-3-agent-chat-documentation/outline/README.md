# Outline (self-hosted) — setup

1. Copy `.env.example` to `.env` and fill in real values:
   - `SECRET_KEY` / `UTILS_SECRET`: `openssl rand -hex 32` (run twice, once per key).
   - `POSTGRES_PASSWORD` / `MINIO_ROOT_PASSWORD`: any strong random string.
   - `CLOUDFLARE_TUNNEL_TOKEN`: create a tunnel at https://one.dash.cloudflare.com/
     (Zero Trust → Networks → Tunnels → Create a tunnel → Docker), point its public
     hostname at `http://outline:3000`, and paste the connector token here.
   - `URL`: the public hostname you assigned to the tunnel (must be `https://`).
2. Start the stack: `docker compose up -d`.
3. Visit the tunnel's public URL, create the first admin account (email/password auth,
   no OAuth provider configured for this POC).
4. Create two Collections representing teams/products, e.g. "Billing" and "Pay", and add
   a few documents to each — these are what the agent will answer questions from.
5. Configure the Outline → agent webhook: Settings → API & Apps → Webhooks → New webhook.
   - URL: `https://<same-tunnel-domain>/webhooks/outline` (the agent service, exposed
     through the same or a second Cloudflare Tunnel — see `../agent/README.md`).
   - Events: `documents.create`, `documents.update`, `documents.publish`,
     `documents.delete`, `documents.archive`.
   - Copy the generated signing secret into `agent/.env` as `OUTLINE_WEBHOOK_SECRET`.
6. Create a personal API token (Settings → API & Apps → New API key) and put it in
   `agent/.env` as `OUTLINE_API_TOKEN`.
