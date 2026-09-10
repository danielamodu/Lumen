-- Lumen Phase 1 system-state tables (Neon / Lakebase Postgres).
--
-- Scope: tenants, used_txs, webhooks + delivery outbox ONLY. Sibyl memory
-- remains the source of truth for all intelligence (COLD journal, WARM
-- patterns, HOT briefs). Every table here holds rebuildable derived or
-- operational state — nothing a delete-Sibyl drill must preserve.
-- Run with the DIRECT (unpooled) URL:  python scripts/migrate.py
-- Idempotent: safe to re-run (CREATE TABLE IF NOT EXISTS).

-- API tenants keyed by SHA-256 of the raw key (raw secret never at rest).
CREATE TABLE IF NOT EXISTS tenants (
    key_hash   TEXT PRIMARY KEY,
    tenant_id  TEXT NOT NULL,
    name       TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    active     BOOLEAN NOT NULL DEFAULT TRUE
);

-- Consumed Base USDC payment hashes (replay protection).
-- The PK is the atomic guard: concurrent reserves race on INSERT, exactly
-- one wins via ON CONFLICT DO NOTHING.
CREATE TABLE IF NOT EXISTS used_txs (
    tx_hash      TEXT PRIMARY KEY,
    used_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    amount_units BIGINT,
    from_address TEXT
);

-- Registered pattern-shift webhooks.
CREATE TABLE IF NOT EXISTS webhooks (
    id           TEXT PRIMARY KEY,
    tenant_id    TEXT NOT NULL,
    user_id      TEXT NOT NULL,
    domain       TEXT NOT NULL,
    callback_url TEXT NOT NULL,
    threshold    DOUBLE PRECISION NOT NULL DEFAULT 0.10,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_fired   TIMESTAMPTZ,
    fire_count   INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS webhooks_tenant_idx ON webhooks (tenant_id);

-- Delivery outbox: check_and_fire ENQUEUES, a worker delivers with retries.
-- status: pending -> delivered | failed (dead-letter after max attempts).
CREATE TABLE IF NOT EXISTS webhook_deliveries (
    id           BIGSERIAL PRIMARY KEY,
    webhook_id   TEXT NOT NULL REFERENCES webhooks (id) ON DELETE CASCADE,
    payload      JSONB NOT NULL,
    status       TEXT NOT NULL DEFAULT 'pending',
    attempts     INTEGER NOT NULL DEFAULT 0,
    next_retry_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_error   TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS webhook_deliveries_due_idx
    ON webhook_deliveries (status, next_retry_at);
