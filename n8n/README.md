# n8n workflows

This folder holds the exported n8n workflows (JSON) and their documentation.

## Export / import
- **Export** (to version it here): open the workflow in n8n → top-right menu (⋯) → **Download** → save the JSON in this folder → commit.
- **Import**: n8n → **Workflows** → **Import from File** → pick the JSON.

## Credentials to create in n8n (Credentials → New)
| Credential | Type | Values |
|---|---|---|
| **Anthropic** | *Header Auth* | Name: `x-api-key` · Value: your `sk-ant-...` key |
| **SmartDesk Postgres** | *Postgres* | Host `postgres` · Port `5432` · Database `smartdesk` · User `smartdesk` · Password `smartdesk` |
| **Jira** *(later)* | *Jira SW Cloud API* | Domain `https://<site>.atlassian.net` · Email · API token |

> Credentials live in n8n, never in the exported JSON — so the workflow files are safe to commit.

## Workflows
| File | Flow | Status |
|---|---|---|
| `smartdesk-core.json` | Manual trigger → sample ticket → Claude triage → Postgres (incident + log) | Day 2A — testable without Jira |
| `smartdesk-full.json` | Jira trigger → Claude triage → write-back → escalate → two-way sync | Day 2B+ |

## AI contract
The triage step sends a ticket to Claude and expects a strict JSON object:
see `claude-triage-request.json` for the exact request body, and
`../ai/triage.py` for the reference implementation (structured outputs).
