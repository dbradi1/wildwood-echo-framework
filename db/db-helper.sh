#!/bin/bash
# Game DB Helper — The Wildwood Echo
# Quick queries for the game database (uses Python sqlite3 since CLI not installed)
# Usage: bash db-helper.sh <command> [args]

DB="${DND_GAME_DB:-$(dirname "$0")/game.db}"

if [ ! -f "$DB" ]; then
  echo "Database not found at $DB"
  exit 1
fi

run_sql() {
  python3 -c "
import sqlite3, sys
conn = sqlite3.connect('$DB')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute('''$1''')
rows = cur.fetchall()
if rows:
    headers = rows[0].keys()
    print('|'.join(headers))
    print('|'.join(['---']*len(headers)))
    for r in rows:
        print('|'.join(str(r[h]) if r[h] is not None else '' for h in headers))
else:
    print('(no results)')
conn.close()
"
}

run_sql_raw() {
  python3 -c "
import sqlite3
conn = sqlite3.connect('$DB')
cur = conn.cursor()
cur.execute('''$1''')
rows = cur.fetchall()
if rows:
    for r in rows:
        print(' | '.join(str(v) if v is not None else '' for v in r))
else:
    print('(no results)')
conn.close()
"
}

case "$1" in
  # Character state
  char|character)
    run_sql "SELECT * FROM character_state ORDER BY id DESC LIMIT 1;"
    ;;
  hp)
    run_sql "SELECT hp_current, hp_max, temp_hp, conditions FROM character_state ORDER BY id DESC LIMIT 1;"
    ;;
  gold)
    run_sql "SELECT gold, silver, copper FROM character_state ORDER BY id DESC LIMIT 1;"
    ;;
  
  # Inventory
  inv|inventory)
    run_sql "SELECT item_name, quantity, notes, magical FROM inventory ORDER BY magical DESC, item_name;"
    ;;
  
  # NPCs
  npcs)
    run_sql "SELECT name, race, role, status, location FROM npcs ORDER BY name;"
    ;;
  npc)
    if [ -z "$2" ]; then echo "Usage: db-helper.sh npc <name>"; exit 1; fi
    run_sql "SELECT * FROM npcs WHERE name LIKE '%${2}%' COLLATE NOCASE;"
    ;;
  
  # Locations
  locations)
    run_sql "SELECT name, region, type FROM locations ORDER BY name;"
    ;;
  
  # Plot threads
  threads|plot)
    run_sql "SELECT title, status, priority, description FROM plot_threads ORDER BY CASE priority WHEN 'red' THEN 1 WHEN 'yellow' THEN 2 WHEN 'green' THEN 3 END, title;"
    ;;
  active-threads)
    run_sql "SELECT title, priority, description FROM plot_threads WHERE status='active' ORDER BY CASE priority WHEN 'red' THEN 1 WHEN 'yellow' THEN 2 WHEN 'green' THEN 3 END;"
    ;;
  
  # Sessions
  sessions)
    run_sql "SELECT session_number, session_date, in_world_day, title, location FROM sessions ORDER BY session_number;"
    ;;
  session)
    if [ -z "$2" ]; then echo "Usage: db-helper.sh session <number>"; exit 1; fi
    run_sql "SELECT * FROM sessions WHERE session_number=$2;"
    ;;
  session-events)
    if [ -z "$2" ]; then echo "Usage: db-helper.sh session-events <session_id>"; exit 1; fi
    run_sql "SELECT event_order, event_type, description, dice_rolls FROM session_events WHERE session_id=$2 ORDER BY event_order;"
    ;;
  
  # Combat log
  combat)
    run_sql "SELECT c.combat_id, s.session_number, c.enemy, c.outcome, c.notable_rolls, c.damage_taken, c.damage_dealt FROM combat_log c JOIN sessions s ON c.session_id = s.session_id ORDER BY c.combat_id;"
    ;;
  
  # Factions
  factions)
    run_sql "SELECT name, alignment, standing_with_nassa FROM factions ORDER BY name;"
    ;;
  
  # World state
  world)
    run_sql "SELECT key, value, notes FROM world_state ORDER BY key;"
    ;;
  
  # Integrity check
  check|integrity)
    run_sql_raw "PRAGMA integrity_check;"
    ;;
  
  # Export everything (backup)
  backup)
    BACKUP_PATH="${DND_BACKUP_DIR:-$(dirname "$DB")}/game-backup-$(date +%Y%m%d-%H%M%S).db"
    cp "$DB" "$BACKUP_PATH"
    echo "Backup created: $BACKUP_PATH"
    ;;
  
  # Schema
  schema)
    python3 -c "
import sqlite3
conn = sqlite3.connect('$DB')
for row in conn.execute(\"SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name\"):
    print(row[0])
    print()
conn.close()
"
    ;;
  
  # Custom query
  query)
    if [ -z "$2" ]; then echo "Usage: db-helper.sh query <SQL>"; exit 1; fi
    run_sql "$2"
    ;;
  
  # Table counts
  counts|stats)
    run_sql "SELECT 'sessions' as tbl, COUNT(*) as cnt FROM sessions UNION ALL SELECT 'character_state', COUNT(*) FROM character_state UNION ALL SELECT 'inventory', COUNT(*) FROM inventory UNION ALL SELECT 'npcs', COUNT(*) FROM npcs UNION ALL SELECT 'locations', COUNT(*) FROM locations UNION ALL SELECT 'factions', COUNT(*) FROM factions UNION ALL SELECT 'plot_threads', COUNT(*) FROM plot_threads UNION ALL SELECT 'session_events', COUNT(*) FROM session_events UNION ALL SELECT 'world_state', COUNT(*) FROM world_state UNION ALL SELECT 'combat_log', COUNT(*) FROM combat_log;"
    ;;
  
  # Help
  help|*)
    cat << 'EOF'
Game DB Helper — The Wildwood Echo
Usage: db-helper.sh <command> [args]

Commands:
  char          — Current character state
  hp            — Current HP/conditions
  gold          — Current gold/silver/copper
  inv           — Full inventory
  npcs          — All NPCs (summary)
  npc <name>    — Single NPC details
  locations     — All locations
  threads       — All plot threads
  active-threads— Active plot threads only
  sessions      — Session list
  session <n>   — Session details
  session-events <id> — Events for a session
  combat        — Combat log
  factions      — Faction standings
  world         — World state key-values
  counts        — Row counts for all tables
  check         — Database integrity check
  backup        — Create a timestamped backup
  schema        — Print database schema
  query <SQL>   — Run custom SQL

Examples:
  db-helper.sh hp
  db-helper.sh npc Pras
  db-helper.sh active-threads
  db-helper.sh query "SELECT * FROM npcs WHERE status='Alive'"
EOF
    ;;
esac