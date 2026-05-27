-- ============================================
-- Initial DB setup — runs once on first docker compose up
-- Enables TimescaleDB. Real tables come in Phase 1 (via Alembic).
-- ============================================

CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Smoke test row so we know the DB is reachable
CREATE TABLE IF NOT EXISTS _bootstrap (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    note TEXT
);

INSERT INTO _bootstrap (note) VALUES ('DB initialized successfully');
