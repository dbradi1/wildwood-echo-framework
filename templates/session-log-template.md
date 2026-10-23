# Session Log Template — The Wildwood Echo

Each session gets a markdown log named `session-NN.md` (zero-padded) in `sessions/`.

```markdown
# Session NN — [Title]

**Date:** YYYY-MM-DD (real-world)
**In-World Day:** Day N
**In-World Time:** time of day
**Location:** where the session took place

## Recap
Where we left off...

## Events
Chronological list of what happened, with dice rolls noted.

## Combat
Any combat encounters, outcomes, damage.

## Discoveries
New information uncovered, lore revealed.

## NPC Interactions
Who the player talked to and what was said.

## Character State (End of Session)
- HP: X/X
- Gold: X GP, X SP, X CP
- Inventory changes
- Conditions
- Location

## Plot Threads Advanced
Which threads moved forward.

## New Threads Opened
Any new plot hooks.

## Cliffhanger
How the session ended — end on a question, not a full stop.

## Next Session Prep
Open questions, possible hooks.
```

## Conventions

- **Dice rolls are recorded in-line** — notable rolls (crits, save-or-suck checks) get named in the Events/Combat sections and mirrored into the `session_events.dice_rolls` and `combat_log.notable_rolls` columns.
- **Cliffhangers are mandatory** whenever possible — the campaign builds session-to-session; end on a decision point.
- **The log is the human-readable source of truth; the database is the queryable mirror.** After each session, the DM updates both (session log first, then `build_db.py`-style inserts or direct SQL via `db-helper.sh query`).
- **In-world time is tracked precisely** (`current_in_world_day`, `in_world_time`, and any ticking clocks in `world_state`) — deadlines like full moons and poisons carry across sessions.