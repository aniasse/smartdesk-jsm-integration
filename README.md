# SmartDesk — AI-Powered Service Management Integration

**English** · [Français](README.fr.md)

A demo integration that connects **Jira Service Management** to an AI triage layer and an external system, with governance built in.

When a ticket is created in **Jira Service Management**, an **n8n** (iPaaS) workflow picks it up, sends it to **Claude** for triage (category, priority, sentiment, summary, suggested reply), writes the result back to Jira, **escalates critical incidents** to an external system (Postgres), and **syncs statuses both ways** — all with **governance** (logging, idempotency, error handling).

> Full project plan: `../projet-technique-valiantys.md`

## Stack
| Layer | Tool | Industry equivalent |
|---|---|---|
| iPaaS | **n8n** (Docker) | Workato / Boomi / Celigo |
| Service desk | **Jira Service Management** | Atlassian / Jira |
| AI layer | **Claude** (structured outputs) | Rovo / Glean |
| External system | **Postgres** | CRM/ERP (Salesforce/NetSuite) |

> The iPaaS concepts here — triggers, connectors, data mapping, error handling — map one-to-one to Workato and Boomi. n8n is the open-source way to demonstrate them.

---

## Day 1 — Setup (~1h)

### 1. Copy the environment file
```bash
cp .env.example .env
# edit .env and fill in the keys (see steps 2 and 3)
```

### 2. Create a free Jira Service Management instance
- Go to **https://www.atlassian.com/software/jira/service-management** → *Get it free*.
- Create a site `https://<your-site>.atlassian.net` and a **Service management** project (key e.g. `SD`).
- Generate an **API token**: https://id.atlassian.com/manage-profile/security/api-tokens
- Fill `.env`: `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`.
- Create **5–6 test tickets** (a bug, a blocked access, a how-to, an outage…).

### 3. Get a Claude API key
- https://console.anthropic.com → API keys.
- Fill `ANTHROPIC_API_KEY` in `.env`.

### 4. Start the infrastructure (n8n + Postgres)
```bash
docker compose up -d
docker compose ps          # both services should be "running"
```
- n8n: **http://localhost:5678** → on first launch, create your owner account (email + password).
- Postgres: `localhost:5432` (smartdesk / smartdesk / smartdesk). The schema is created automatically.

### 5. Test the AI layer in isolation
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r ai/requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...        # or: set -a; source .env; set +a
python ai/triage.py
```
You should see a JSON object: `{category, priority, sentiment, summary, suggested_reply}`.
Test with your own ticket too:
```bash
echo '{"subject":"Billing wrong amount","body":"I was charged twice this month."}' | python ai/triage.py
```

✅ **End of Day 1:** infrastructure running + AI triage working. Next days (see the plan): build the n8n workflow (Jira trigger → AI → write-back → Postgres/Slack escalation → two-way sync) + governance.

---

## Connections used in n8n
- **Jira**: "Jira SW Cloud API" credential → `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`.
- **Postgres**: host `postgres` (the Docker service name), port `5432`, db/user/pass `smartdesk`.
- **AI**: an *HTTP Request* node (POST `https://api.anthropic.com/v1/messages`, headers `x-api-key`, `anthropic-version: 2023-06-01`) — replicating the logic of `ai/triage.py`.

## Structure
```
smartdesk-jsm-integration/
├── docker-compose.yml      # n8n + Postgres
├── .env.example            # secrets to fill in
├── db/init.sql             # tables: incidents, integration_logs, processed_events
├── ai/
│   ├── triage.py           # AI layer (Claude structured outputs)
│   └── requirements.txt
└── README.md
```
