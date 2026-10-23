# Game Database

The campaign state backend is a single-file **SQLite** database (`game.db`), built from `db/schema.sql` and populated by `db/build_db.py`. It exists so the DM can *query* state — "what's in Nassa's inventory?", "which plot threads are red?", "how much gold do we have?" — without grepping prose files.

## Design: Markdown first, database as mirror

The authoritative narrative state lives in markdown files that the DM agent reads every session:

| File | Contents |
|---|---|
| `character.md` | Current HP, gold, inventory, conditions, location |
| `campaign/dm-reference.md` | Full DM notes — NPCs, locations, plot threads, open questions |
| `campaign/npcs.md` | NPC roster |
| `campaign/gm-suggestions.md` | Pacing/coaching notes |
| `sessions/session-NN.md` | One structured log per play session |

The database is a **queryable projection** of those files. If they disagree, the markdown wins and the DB is rebuilt. `build_db.py` does a full drop-and-rebuild (`os.remove` + re-execute schema + re-insert everything) precisely so the DB can never drift from the notes — it's disposable by design.

## Schema (11 tables)

- **`sessions`** — one row per play session: real-world date, in-world day/time, title, summary, location, cliffhanger
- **`character_state`** — per-session snapshot: HP, temp HP, AC, ki points, coin (gold/silver/copper), inspiration, exhaustion, conditions, death saves, location
- **`inventory`** — items with quantity, notes, `magical` flag, and acquisition source
- **`npcs`** — full roster: race, class, role, status, location, relationship, first/last-seen session, appearance, personality, equipment, motivation
- **`locations`** — discovered places with region, type, description, `discovered_session`
- **`factions`** — alignment, goals, `standing_with_nassa`
- **`plot_threads`** — title, status (`active`/`dormant`/`resolved`), priority (`red`/`yellow`/`green`), opened/resolved session
- **`session_events`** — ordered event log per session: type (`combat`/`social`/`exploration`/`lore`/`discovery`/`decision`), description, dice rolls, consequences
- **`combat_log`** — per-fight record: enemy, outcome, notable rolls, damage taken/dealt
- **`world_state`** — key-value store for live world facts (`current_in_world_day`, `vaelthyr_binding_status`, `days_remaining_to_full_moon`, ticking clocks, NPC statuses)

All writes go through `PRAGMA foreign_keys = ON` (character_state, session_events, and combat_log reference `sessions`).

## Build

```bash
python3 db/build_db.py        # env: DND_GAME_DB (default: db/game.db)
```

Note: the campaign build script seeds the DB from actual play history — sessions, NPCs, threads — so a rebuild is a faithful re-materialization, not data loss.

## Querying: db-helper.sh

`sqlite3` CLI is not installed on the host, so `db/db-helper.sh` shells out to `python3 -c` with the stdlib `sqlite3` module instead. Output is markdown-table formatted for reading in chat.

```bash
DB="..." bash db/db-helper.sh <command>

  char            current character state          hp       HP/conditions
  gold            coin on hand                    inv      inventory (magical first)
  npcs            NPC roster summary              npc <name>   one NPC, full detail
  locations       discovered places               factions     standings with the PC
  threads         all plot threads (red first)   active-threads  active only
  sessions        session list                    session <n>  one session
  session-events <id>  ordered events             combat    fight log
  world           world_state key-values          counts    row counts per table
  check           PRAGMA integrity_check          backup    timestamped .db copy
  schema          print schema                    query <SQL>  arbitrary SQL
```

Env: `DND_GAME_DB` (default `db/game.db` next to the script), `DND_BACKUP_DIR` for `backup`.

## In-world time & ticking clocks

The `world_state` table carries the campaign calendar. At session start the DM reads it and tells the player what time remains on every active clock — a fraying binding, a poison, a full-moon deadline. The clock is a storytelling tool, not a punishment: don't rush the player past moments that matter, but let the pressure be real. The nightly checkpoint (see `docs/nightly-save-automation.md`) watches these files between sessions so nothing drifts unnoticed.