-- The Wildwood Echo — Campaign Database Schema
-- D&D 5e Campaign Tracker

PRAGMA foreign_keys = ON;

-- Sessions: one row per game session
CREATE TABLE IF NOT EXISTS sessions (
    session_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    session_number  INTEGER,
    session_date    TEXT,       -- real-world date ISO format
    in_world_day    INTEGER,
    in_world_time   TEXT,
    title           TEXT,
    summary         TEXT,
    location        TEXT,
    cliffhanger     TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Character state snapshot per session
CREATE TABLE IF NOT EXISTS character_state (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id              INTEGER REFERENCES sessions(session_id),
    hp_current              INTEGER,
    hp_max                  INTEGER,
    temp_hp                 INTEGER,
    ac                      INTEGER,
    gold                    INTEGER,
    silver                  INTEGER,
    copper                  INTEGER,
    ki_current              INTEGER,
    ki_max                  INTEGER,
    inspiration             INTEGER,
    exhaustion              INTEGER,
    conditions              TEXT,   -- comma separated or empty
    death_saves_success     INTEGER,
    death_saves_failure     INTEGER,
    location                TEXT,
    updated_at              TEXT DEFAULT (datetime('now'))
);

-- Inventory items
CREATE TABLE IF NOT EXISTS inventory (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name   TEXT,
    quantity    INTEGER,
    notes       TEXT,
    magical     INTEGER DEFAULT 0,
    source      TEXT
);

-- NPCs
CREATE TABLE IF NOT EXISTS npcs (
    npc_id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                    TEXT,
    race                    TEXT,
    class                   TEXT,
    role                    TEXT,
    status                  TEXT,
    location                TEXT,
    relationship            TEXT,
    first_appearance_session INTEGER,
    last_seen_session       INTEGER,
    notes                   TEXT,
    appearance              TEXT,
    personality             TEXT,
    equipment               TEXT,
    motivation              TEXT
);

-- Locations
CREATE TABLE IF NOT EXISTS locations (
    location_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT,
    region              TEXT,
    type                TEXT,
    description         TEXT,
    discovered_session  INTEGER,
    notes               TEXT
);

-- Factions
CREATE TABLE IF NOT EXISTS factions (
    faction_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT,
    alignment           TEXT,
    goals               TEXT,
    standing_with_nassa TEXT,
    notes               TEXT
);

-- Plot threads
CREATE TABLE IF NOT EXISTS plot_threads (
    thread_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title              TEXT,
    status             TEXT,   -- active/dormant/resolved
    priority           TEXT,   -- red/yellow/green
    description        TEXT,
    opened_session     INTEGER,
    resolved_session   INTEGER,
    notes              TEXT
);

-- Session events (detailed event log per session)
CREATE TABLE IF NOT EXISTS session_events (
    event_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  INTEGER REFERENCES sessions(session_id),
    event_order INTEGER,
    event_type  TEXT,   -- combat/social/exploration/lore/discovery/decision
    description TEXT,
    dice_rolls  TEXT,
    consequences TEXT
);

-- World state key-value store
CREATE TABLE IF NOT EXISTS world_state (
    key         TEXT PRIMARY KEY,
    value       TEXT,
    updated_at  TEXT DEFAULT (datetime('now')),
    notes       TEXT
);

-- Combat log
CREATE TABLE IF NOT EXISTS combat_log (
    combat_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      INTEGER REFERENCES sessions(session_id),
    enemy           TEXT,
    outcome         TEXT,
    notable_rolls   TEXT,
    damage_taken    INTEGER,
    damage_dealt    INTEGER,
    notes           TEXT
);