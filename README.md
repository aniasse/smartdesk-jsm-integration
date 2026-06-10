# SmartDesk — AI-Powered Service Management Integration

Intégration de démonstration pour les entretiens techniques **Valiantys**.
Quand un ticket arrive dans **Jira Service Management**, un workflow **n8n** (iPaaS)
le récupère, le fait **trier par une IA (Claude)**, réécrit le résultat dans Jira,
**escalade les incidents critiques** vers un système externe (Postgres), et
**synchronise les statuts dans les deux sens** — le tout avec **gouvernance**
(logs, idempotence, gestion d'erreurs).

> Plan détaillé du projet : `../projet-technique-valiantys.md`

## Stack (= les outils de Valiantys)
| Brique | Outil | Équivalent Valiantys |
|---|---|---|
| iPaaS | **n8n** (Docker) | Workato / Boomi / Celigo |
| Système métier | **Jira Service Management** | Atlassian / Jira |
| Couche IA | **Claude** (structured outputs) | Rovo / Glean |
| Système externe | **Postgres** | CRM/ERP (Salesforce/NetSuite) |

---

## Jour 1 — Setup (≈ 1h)

### 1. Cloner les variables d'environnement
```bash
cp .env.example .env
# édite .env et renseigne les clés (voir étapes 2 et 3)
```

### 2. Créer une instance Jira Service Management gratuite
- Va sur **https://www.atlassian.com/software/jira/service-management** → *Get it free*.
- Crée un site `https://<ton-site>.atlassian.net` et un projet **Service Management** (clé ex. `SD`).
- Génère un **API token** : https://id.atlassian.com/manage-profile/security/api-tokens
- Renseigne dans `.env` : `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`.
- Crée **5-6 tickets de test** (un bug, un accès bloqué, une question, une panne…).

### 3. Récupérer une clé API Claude
- https://console.anthropic.com → API keys.
- Renseigne `ANTHROPIC_API_KEY` dans `.env`.

### 4. Lancer l'infra (n8n + Postgres)
```bash
docker compose up -d
docker compose ps          # les 2 services doivent être "running"
```
- n8n : **http://localhost:5678** (admin / changeme — change le mot de passe dans le compose).
- Postgres : `localhost:5432` (smartdesk / smartdesk / smartdesk). Le schéma est créé tout seul.

### 5. Tester la couche IA en isolé
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r ai/requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...        # ou: set -a; source .env; set +a
python ai/triage.py
```
Tu dois voir un JSON `{category, priority, sentiment, summary, suggested_reply}`.
Teste aussi avec ton propre ticket :
```bash
echo '{"subject":"Billing wrong amount","body":"I was charged twice this month."}' | python ai/triage.py
```

✅ **Fin du Jour 1 :** infra qui tourne + triage IA fonctionnel. Les jours suivants
(voir le plan) : construire le workflow n8n (trigger Jira → IA → write-back →
escalade Postgres/Slack → sync bidirectionnelle) + gouvernance.

---

## Connexions à utiliser dans n8n
- **Jira** : credential "Jira SW Cloud API" → `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`.
- **Postgres** : host `postgres` (nom du service Docker), port `5432`, db/user/pass `smartdesk`.
- **IA** : node *HTTP Request* (POST `https://api.anthropic.com/v1/messages`, headers
  `x-api-key`, `anthropic-version: 2023-06-01`) — réplique la logique de `ai/triage.py`.

## Structure
```
smartdesk-jsm-integration/
├── docker-compose.yml      # n8n + Postgres
├── .env.example            # secrets à renseigner
├── db/init.sql             # tables: incidents, integration_logs, processed_events
├── ai/
│   ├── triage.py           # couche IA (Claude structured outputs)
│   └── requirements.txt
└── README.md
```
