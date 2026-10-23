# Nightly Save & Session Review Automation

The framework has a two-layer safety net between sessions: a deterministic **shell checkpoint** that watches the files, and an **agent save job** that runs nightly, reviews state, and writes the daily memory log. Together they guarantee the campaign never drifts, never loses an evening's play, and always resumes with full context.

## Layer 1 — nightly-checkpoint.sh (deterministic)

`automation/nightly-checkpoint.sh` runs via cron at 11 PM ET. It is deliberately dumb — no AI, just file mtime comparisons and flag management:

1. Compares mtimes of the state files (`character.md`, `dm-reference.md`, `npcs.md`) against the last recorded run (`.last-checkpoint` timestamp).
2. Appends a structured line-by-line report to `nightly-checkpoint.log` (session log count, whether today has a memory file, DB existence/size).
3. If state changed since the last run, writes a **`.checkpoint-pending` flag file** — the signal that a session log update or DB sync may be needed.
4. If nothing changed, *removes* the pending flag and logs "game state stable."

The flag file is the interlock: the agent-side job checks for it, and the script is the only thing allowed to set/clear it. Failures leave the flag standing, so a broken run is self-reporting on the next pass.

```bash
# cron entry (America/New_York)
0 23 * * * DND_WORKSPACE=/path/to/workspace automation/nightly-checkpoint.sh
```

Env: `DND_WORKSPACE` (default `$HOME/.openclaw/workspace/dandd`).

## Layer 2 — Nightly Game Save (agent job)

The same 11 PM cron slot also triggers an **OpenClaw automation** ("Nightly Game Save — Wildwood Echo") that wakes the DM agent itself with a save prompt. The agent's nightly review loop:

1. **Re-read state** — character sheet, DM reference, session logs, DB size/mtime.
2. **Check for a `.checkpoint-pending` flag** — if set (or if a session was played today), write up the changes: new session log or updates to the existing one, character state, plot threads, DB rows.
3. **Write the daily memory file** (`memory/YYYY-MM-DD.md`) — a save-game summary: what happened, current HP/gold/location, in-world day, ticking clocks remaining, no-play streak if idle.
4. **Verify the database** — size and modification time (the host has no `sqlite3` CLI, so `db-helper.sh check` shells out to Python's stdlib module for integrity when needed).
5. **Clear the pending flag** once changes are recorded.
6. If nothing happened, write a short "no session today — state stable" entry. Even absence is logged, because the streak counter ("N days since last session") is itself tracked and reported.

One operational lesson baked into the prompt: the daily memory file must be **created with a write, not edited** — an edit step against a not-yet-existing file fails the whole run. The save prompt explicitly uses create-or-overwrite semantics for the daily file.

## Session review loop (per-play-session)

When a session actually happens, the flow is:

1. **Run the session** — the DM plays live with the player; all dice for the player's character are rolled by the player, never by the DM.
2. **Write the session log** (`sessions/session-NN.md`, template in `templates/session-log-template.md`) — recap, events, combat, discoveries, NPC interactions, end-state, cliffhanger, next-session prep.
3. **Update the markdown state files** — character sheet first (HP, gold, inventory, conditions, location), then DM reference and NPC roster.
4. **Sync the database** — insert the session row, character_state snapshot, session_events, combat_log entries, and update `world_state` clocks (in-world day, time, deadlines).
5. **Update the ticking clocks** — every active timer (poisons, full moons, rituals) carries forward explicitly; the next session opens by telling the player what time remains.

The nightly checkpoint then verifies all of this stayed consistent, night after night, until the next session.

## Why two layers?

The shell script is incorruptible — it can't hallucinate, skip a night, or misread state. The agent job can *interpret* — it knows whether a file change means "session played" vs. "campaign reboot restructure" and writes prose accordingly. The script watches; the agent narrates; the flag file keeps them honest to each other.