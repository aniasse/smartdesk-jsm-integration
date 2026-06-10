-- SmartDesk — schéma du "système externe" (stand-in CRM/ERP) + gouvernance
-- Exécuté automatiquement au premier démarrage de Postgres.

-- 1) Les incidents escaladés (= système de référence externe)
CREATE TABLE IF NOT EXISTS incidents (
    id          SERIAL PRIMARY KEY,
    jira_key    TEXT UNIQUE NOT NULL,
    summary     TEXT,
    category    TEXT,
    priority    TEXT,
    sentiment   TEXT,
    ai_summary  TEXT,
    status      TEXT NOT NULL DEFAULT 'Open',     -- Open | Resolved
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2) Observabilité : une ligne par étape exécutée (logs + latence IA)
CREATE TABLE IF NOT EXISTS integration_logs (
    id            SERIAL PRIMARY KEY,
    jira_key      TEXT,
    event_type    TEXT,        -- ex: issue_created, status_synced
    step          TEXT,        -- ex: ai_triage, write_back, escalate
    status        TEXT,        -- success | error
    detail        TEXT,
    ai_latency_ms INTEGER,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3) Idempotence : empêche de traiter deux fois le même événement
CREATE TABLE IF NOT EXISTS processed_events (
    idempotency_key TEXT PRIMARY KEY,   -- ex: "SD-42:issue_created"
    jira_key        TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
