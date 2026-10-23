#!/bin/bash
# Nightly Game Save — The Wildwood Echo
# Checks for changes to game state files and updates session logs + daily memory
# Run via cron at 11 PM ET

WORKSPACE="${DND_WORKSPACE:-$HOME/.openclaw/workspace/dandd}"
SESSIONS_DIR="$WORKSPACE/sessions"
CHARACTER_FILE="$WORKSPACE/projects/dnd/character.md"
DM_REF_FILE="$WORKSPACE/dnd/campaign/dm-reference.md"
NPCS_FILE="$WORKSPACE/dnd/campaign/npcs.md"
DB_FILE="$WORKSPACE/dnd/game.db"
MEMORY_DIR="$WORKSPACE/memory"
LOG_FILE="$WORKSPACE/dnd/nightly-checkpoint.log"
LAST_RUN_FILE="$WORKSPACE/dnd/.last-checkpoint"

TODAY=$(date +%Y-%m-%d)
NOW=$(date -Iseconds)

echo "[$NOW] Nightly checkpoint started" >> "$LOG_FILE"

# Check if game state files have changed since last run
changed=false

if [ -f "$LAST_RUN_FILE" ]; then
  last_run=$(cat "$LAST_RUN_FILE")
  for f in "$CHARACTER_FILE" "$DM_REF_FILE" "$NPCS_FILE"; do
    if [ -f "$f" ]; then
      file_time=$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null)
      if [ "$file_time" -gt "$last_run" ]; then
        changed=true
        echo "[$NOW] Changed: $f" >> "$LOG_FILE"
      fi
    fi
  done
else
  # First run — no changes to log, just record state
  changed=false
  echo "[$NOW] First run — recording baseline state" >> "$LOG_FILE"
fi

# Record this run time
date +%s > "$LAST_RUN_FILE"

# Count existing session logs
session_count=$(ls "$SESSIONS_DIR"/session-*.md 2>/dev/null | wc -l)
echo "[$NOW] Session logs found: $session_count" >> "$LOG_FILE"

# Check if today's memory file exists
memory_file="$MEMORY_DIR/$TODAY.md"
if [ ! -f "$memory_file" ]; then
  echo "[$NOW] No memory file for today ($TODAY) — no game activity to log" >> "$LOG_FILE"
else
  echo "[$NOW] Memory file exists for today" >> "$LOG_FILE"
fi

# If files changed, signal that a session log update may be needed
if [ "$changed" = true ]; then
  echo "[$NOW] ⚠️  Game state files changed since last checkpoint!" >> "$LOG_FILE"
  echo "[$NOW] Review needed: check if session log #$session_count covers today's changes" >> "$LOG_FILE"
  # Create a flag file that the agent can check
  echo "$NOW" > "$WORKSPACE/dnd/.checkpoint-pending"
else
  echo "[$NOW] No changes detected — game state stable" >> "$LOG_FILE"
  # Remove pending flag if it exists
  rm -f "$WORKSPACE/dnd/.checkpoint-pending"
fi

# Verify database exists
if [ -f "$DB_FILE" ]; then
  db_size=$(stat -c %s "$DB_FILE" 2>/dev/null || stat -f %z "$DB_FILE" 2>/dev/null)
  echo "[$NOW] Database OK: $DB_FILE ($db_size bytes)" >> "$LOG_FILE"
else
  echo "[$NOW] ⚠️  Database missing: $DB_FILE" >> "$LOG_FILE"
fi

echo "[$NOW] Nightly checkpoint complete" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"