# Wildwood Echo Framework

The campaign-engine framework behind **The Wildwood Echo**, an AI-DM'd D&D 5e campaign: a SQLite game-state backend, a nightly save/checkpoint automation with an agent-driven session review loop, and structured session-log templates. Built to be self-consistent — the world never drifts, nothing is lost between sessions, and the next session always resumes with full context.

## What it is

A solo campaign runs on three moving parts:

1. **Game state** — markdown files are the source of truth (character sheet, DM reference, NPC roster, session logs). A single-file **SQLite** database mirrors them for fast querying: 11 tables covering sessions, character snapshots, inventory, NPCs, locations, factions, plot threads, event logs, combat, and a key-value `world_state` for in-world time and ticking clocks.
2. **Nightly save** — a deterministic shell checkpoint (mtime comparison + pending-flag management) plus a nightly AI-agent save job that reviews state, writes session logs and daily memory, and verifies the database. Two layers: the script watches, the agent narrates, a `.checkpoint-pending` flag keeps them honest.
3. **Session review loop** — after each play session: write the structured session log → update character sheet and DM notes → sync the database → carry every ticking clock (full moons, poisons, rituals) forward explicitly.

```
markdown state files (source of truth)
        │
        ├── character.md ─ HP/gold/inventory/conditions
        ├── campaign/dm-reference.md, npcs.md, gm-suggestions.md
        └── sessions/session-NN.md (structured logs)
        │
        ▼  build_db.py (drop & rebuild — disposable by design)
┌─────────────────────────────┐
│  game.db (SQLite, 11 tables) │◄── db-helper.sh (query/backup/integrity)
└─────────────────────────────┘
        ▲
        │ mtime watch + .checkpoint-pending flag
automation/nightly-checkpoint.sh (cron, 11 PM)
        +
Nightly agent save job (session review, daily memory write)
```

## Repository layout

```
db/
  schema.sql               # 11-table campaign schema
  build_db.py              # full rebuild from play history (env: DND_GAME_DB)
  db-helper.sh             # query CLI via Python stdlib sqlite3 (no sqlite3 binary needed)
automation/
  nightly-checkpoint.sh    # mtime watch + pending-flag interlock (env: DND_WORKSPACE)
templates/
  session-log-template.md  # structured per-session log format
docs/
  database.md              # schema design, markdown-first philosophy, query cookbook
  nightly-save-automation.md   # the two-layer nightly save + agent review loop
```

## Quick start

```bash
# build the database from schema + play history
python3 db/build_db.py

# query it
bash db/db-helper.sh hp
bash db/db-helper.sh active-threads
bash db/db-helper.sh npc "Pras"

# install the nightly checkpoint (cron, 11 PM ET)
0 23 * * * DND_WORKSPACE=/path/to/workspace /path/to/automation/nightly-checkpoint.sh
```

## Design principles

- **Markdown first, database as mirror.** The DM thinks in prose; the DB is a disposable projection. If they disagree, markdown wins and the DB is rebuilt.
- **Ticking clocks are first-class.** `world_state` carries the campaign calendar and every deadline. Sessions open by telling the player exactly what time remains — the clock is a storytelling tool, not a punishment.
- **Absence is logged.** Even "no session today — state stable" gets a nightly entry; the no-play streak is tracked and surfaced so momentum is visible.
- **Incorruptible watcher + interpretive writer.** The shell checkpoint can't hallucinate; the agent job can understand *why* files changed. Each covers the other's weakness.
- **Zero exotic dependencies.** Python stdlib + bash + cron. No frameworks, no servers.

## Campaign context

Built for *The Wildwood Echo* — a homebrew high-fantasy 5e campaign (low-magic-but-deep world, ancient bindings, skin-changers) run by an OpenClaw DM agent for a single player. The framework itself is campaign-agnostic: swap the seeded history in `build_db.py`, keep the machinery.

## License

MIT — do whatever you want, no warranty. Not affiliated with Wizards of the Coast.