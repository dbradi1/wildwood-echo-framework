#!/usr/bin/env python3
"""Build The Wildwood Echo campaign SQLite database."""
import sqlite3
import os
from datetime import datetime

import os
DB_PATH = os.environ.get("DND_GAME_DB", os.path.join(os.path.dirname(__file__), "game.db"))
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

# Remove existing DB for clean rebuild
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

# Load schema
with open(SCHEMA_PATH, "r") as f:
    schema_sql = f.read()
cur.executescript(schema_sql)

now = datetime.now().isoformat()

# ─── SESSIONS ───
sessions = [
    # (session_number, session_date, in_world_day, in_world_time, title, summary, location, cliffhanger, created_at)
    (0, None, None, None, "Session Zero — Identity & Character Creation",
     "Echo established as DM; campaign named 'The Wildwood Echo'. Nassa created: Wood Elf Monk 1, CON 8, Soldier background. Backstory seeded: Wildwood Wardens, Green-Leaf Sentinels, Emerald Enclave.",
     None, None, now),
    (1, None, 3, "late afternoon", "Session 1 — Thornhaven (Wolf Hunt & Well)",
     "Nassa arrived in Thornhaven; met Ketric and Vera at the Hare & Hound. Investigated wolf threat — Changed skin-walkers operating from the old watchtower. Found Pras alive in an iron cage in the cellar. Alpha wolf killed by Ketric's crit. Changed Leader escaped. Investigated the well north of town; discovered Vaelthyr bound beneath — ancient Fey lord sealed by a covenant requiring a living keeper's blood. The binding is fraying. Full moon Day 6 is the likely deadline. Travelled south with Pras to a Warden waystation.",
     "Warden waystation, south of Thornhaven",
     "At the waystation door — occupied, door marked 'Come in peace or don't come at all'. Decision point: enter or move on?",
     now),
]

cur.executemany("""
    INSERT INTO sessions (session_number, session_date, in_world_day, in_world_time,
                          title, summary, location, cliffhanger, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", sessions)

# Get session IDs
session0_id = cur.execute("SELECT session_id FROM sessions WHERE session_number=0").fetchone()[0]
session1_id = cur.execute("SELECT session_id FROM sessions WHERE session_number=1").fetchone()[0]

# ─── CHARACTER STATE ───
# Current state (end of Session 1)
char_state = (
    session1_id,
    7,   # hp_current
    7,   # hp_max
    0,   # temp_hp
    14,  # ac
    27,  # gold
    11,  # silver
    5,   # copper
    1,   # ki_current (Monk level 1 — actually ki unlocks at level 2, but sheet says 1/1)
    1,   # ki_max
    0,   # inspiration
    0,   # exhaustion
    "",  # conditions
    0,   # death_saves_success
    0,   # death_saves_failure
    "Warden waystation, south of Thornhaven",
    now,
)
cur.execute("""
    INSERT INTO character_state (session_id, hp_current, hp_max, temp_hp, ac,
        gold, silver, copper, ki_current, ki_max, inspiration, exhaustion,
        conditions, death_saves_success, death_saves_failure, location, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", char_state)

# ─── INVENTORY ───
inventory = [
    ("Spear", 1, "Versatile (1d6/1d8), thrown 20/60", 0, "Starting equipment"),
    ("Darts", 10, "Thrown (20/60)", 0, "Starting equipment"),
    ("Explorer's Pack", 1, "Backpack, bedroll, mess kit, tinderbox, 10 torches, 10 days rations, waterskin, 50 ft hempen rope", 0, "Starting equipment"),
    ("Insignia of Rank", 1, "Wildwood Wardens", 0, "Starting equipment"),
    ("Tattered Enemy Banner", 1, "Trophy from a fallen foe", 0, "Starting equipment"),
    ("Deck of Cards", 1, "", 0, "Starting equipment"),
    ("Common Clothes", 1, "One set", 0, "Starting equipment"),
    ("Lute", 1, "", 0, "Starting equipment"),
    ("Healing Potion (dwarven)", 2, "2d4+2 each", 0, "Madam Olara, Thornhaven"),
    ("Healer's Kit", 1, "10 uses", 0, "Madam Olara, Thornhaven"),
    ("Iron Pitons", 4, "Gift from Corra — contract to bring Pras back", 0, "Corra, Thornhaven"),
    ("Silver Chain", 1, "Gift from Corra — contract to bring Pras back", 0, "Corra, Thornhaven"),
]
cur.executemany("""
    INSERT INTO inventory (item_name, quantity, notes, magical, source)
    VALUES (?, ?, ?, ?, ?)
""", inventory)

# ─── NPCs ───
npcs = [
    # Pras
    ("Pras", "Half-elf", "Rogue (scout/fixer)", "Hired guide and current traveling companion",
     "With Nassa at the Warden waystation, south of Thornhaven",
     "Warden waystation, south of Thornhaven",
     "Paid 5 GP for aid. Loyal so far, though maybe still figuring out why.",
     1, 1,
     "Original canon — was a Thornhaven town guard and tracker on the patrol that ran into the Changed. Bought time so Corra and Fen could escape. Presumed dead, found alive in an iron cage in the cellar of the old watchtower. Voice destroyed from captivity. Recovering at the Hare & Hound before joining Nassa south.",
     "Mid-thirties, softened by elven blood. Sandy brown hair, cropped short. Green eyes that check exits before faces. Patched traveler's coat over worn leathers. Moves quiet.",
     "Friendly, but deflection is a reflex. Jokes past personal questions. Nassa might be the first person in a long time who paid him for honest work.",
     "Guard's short sword, dagger, lantern, traveler's coat",
     "Curiosity, the 5 GP, and maybe something he hasn't admitted to himself yet."),
    # Ketric Bronzebeard
    ("Ketric Bronzebeard", "Dwarf (Clan Bronzebeard)", "Fighter", "Ally from the wolf hunt",
     "Alive, last seen at the Hare & Hound after the watchtower mission",
     "Thornhaven — the Hare & Hound (last known)",
     "Grudging comrade. Fought alongside Nassa against the Changed. Not warm, but solid.",
     1, 1,
     "Landed a nat-20 critical on the alpha wolf for 20 damage. Disappeared after the mission — said he 'had something to do.' Vera is holding 16 gp for him. Knows dwarven oral tradition about the Changed — calls them by an older dwarvish name. War-cry: 'Nékhed.'",
     "Red beard braided with iron rings. Built like a keg of nails. Voice like gravel sliding downhill.",
     "Taciturn loner. Doesn't trust easy, but once you're in, you're in.",
     "Warhammer named Brünhilda, leather roll of thieves' tools",
     "Unknown — left after the watchtower mission saying he 'had something to do.'"),
    # Vera
    ("Vera", "Human", "Ranger (implied)", "Ally from the wolf hunt",
     "Alive, last seen at the Hare & Hound after the mission",
     "Thornhaven — the Hare & Hound (last known)",
     "Pragmatic planner. Recognized Nassa's soldier background immediately. Mutual respect.",
     1, 1,
     "Holding Ketric's 16 gp. Knocked out the cellar guard in the watchtower cellar. Does hunting, tracking, and work for the town council.",
     "Early twenties, dark hair pulled back, brown eyes, scar along her jaw. Leather armor that's seen real use.",
     "Ex-soldier instincts. The one who thinks three steps ahead.",
     "Short sword, dagger",
     "Pragmatic — works for the town council as a hunter/tracker."),
    # Marta
    ("Marta", "Human", None, "Barkeep of the Hare & Hound",
     "Alive, running the inn in Thornhaven",
     "Thornhaven — the Hare & Hound",
     "Warm but sharp. Gave Nassa the non-stranger room rate because Vera vouched.",
     1, 1,
     "Knows everyone's business in Thornhaven.",
     "Fifties, silver-streaked red hair, heavyset.",
     "Knows everyone's business. Warm but sharp.",
     None, None),
    # Corra
    ("Corra", "Human", None, "Town guard — sole survivor of the patrol (with Fen)",
     "Alive, recovering in Thornhaven. Nightmares.",
     "Thornhaven",
     "Gave Nassa iron pitons and a silver chain as a gift — and a contract. 'Bring Pras back.' Genuine grief. That debt is still open.",
     1, 1,
     "Nassa still carries the pitons and chain. Pras is alive and with Nassa — Corra doesn't know yet.",
     "Early thirties, dark hair cut short.",
     "Genuine grief. Nightmares from the patrol.",
     None, "Wants Pras back alive. Gave Nassa the contract."),
    # Fen
    ("Fen", "Human", None, "Town guard — survived the patrol with Corra",
     "Alive, in Thornhaven. Won't talk about what happened.",
     "Thornhaven",
     "'Don't bother him.'",
     1, 1,
     "Survived the patrol but won't discuss it.",
     None, "Silent, traumatized.",
     None, None),
    # Patchy Beard
    ("Patchy Beard", "Human", None, "Older gate guard, stocky",
     "Alive",
     "Thornhaven gate",
     "Knew of the Wildwood Wardens by reputation. Tested Nassa's claimed background by asking about the banner. Let him through with soldier's respect.",
     1, 1,
     None, "Stocky, older.",
     "Knew the Wildwood Wardens by reputation. Soldier's respect.",
     None, None),
    # Younger Guard
    ("Younger Guard", "Human", None, "Gate guard, thin, barely more than a teen",
     "Alive",
     "Thornhaven gate",
     "Curious about the Wardens — asked whether they really fight bare-handed.",
     1, 1,
     None, "Thin, barely more than a teen.",
     "Curious, enthusiastic about the Wardens.",
     None, None),
    # Madam Olara
    ("Madam Olara", "Human", None, "Herbalist/healer",
     "Alive, shop in Thornhaven",
     "Thornhaven — herbalist shop",
     "Sold Nassa healing potions and healer's kit. Treated Nassa's wolf venom.",
     1, 1,
     "Sells healing potions (45 gp each), can treat wolf venom. Had a notice posted for herbs wanted.",
     None, "Professional healer.",
     None, "Business — selling potions and healing services."),
    # Del
    ("Del", "Human", None, "Town guard on the patrol",
     "KIA. Did not make it out.",
     None,
     "Fallen comrade from the patrol.",
     1, 1,
     "Killed in action on the patrol that encountered the Changed.",
     None, None,
     None, None),
    # Vaelthyr
    ("Vaelthyr", "Ancient Fey (lord)", None, "Primary antagonist — imprisoned beneath the well north of Thornhaven",
     "Bound but stirring. Binding is fraying.",
     "Beneath the well north of Thornhaven",
     "None yet — not encountered directly.",
     1, 1,
     "Covenantal binding — requires a living keeper's blood to maintain. Wards are in pre-Elvish. When the seal breaks, the well stops giving and starts taking — pulls everything nearby into itself. Thornhaven is in the danger zone (~2 hours away). Deadline: full moon, Day 6 (~3 days). Unknowns: What court? What was the crime? Why prison instead of execution?",
     "Ancient Fey lord — alien, of an older order. Fey logic, not mortal logic.",
     "Fey lord — motivations unknown.",
     None, "Bound but stirring. The binding is fraying."),
    # The Keeper
    ("The Keeper", "Unknown", None, "Unknown figure maintaining Vaelthyr's binding with their own blood",
     "Unknown — alive, dead, or failing",
     None,
     "None yet",
     1, 1,
     "Identity, location, whether they want to be found — all unknown. The geometric wards are pre-Elvish.",
     "Unknown.",
     "Unknown.",
     None, "Unknown — maintaining the binding? Or failing?"),
    # Changed Leader
    ("The Changed Leader", "Humanoid", None, "Commander of the wolf pack — Changed skin-walker",
     "Unaccounted for — escaped after the alpha wolf was killed",
     None,
     "Enemy — escaped. Unaccounted for.",
     1, 1,
     "Humanoid figure in a dark cloak. Commanded the wolf pack with hand signals. Escaped after the alpha wolf died.",
     "Dark cloak. Commands wolves with hand signals.",
     "Chooses to shift — wears skins like clothes. Not a lycanthrope.",
     None, "Unknown — commands the Changed and wolf packs."),
    # Cellar Guard
    ("Cellar Guard", "Human", None, "Human follower of the Changed — guard in the watchtower cellar",
     "Dead — killed by Ketric in combat",
     "Old watchtower cellar (near Thornhaven)",
     "Enemy — killed.",
     1, 1,
     "Wore a wolf-claw talisman. Branded on the wrist with a geometric symbol (Changed mark?). The brand may connect to Vaelthyr's wards — pre-Elvish geometric patterns on the well. Unconfirmed.",
     "Wolf-claw talisman. Geometric brand on wrist.",
     "Follower of the Changed.",
     "Wolf-claw talisman",
     "Guarding the cellar where Pras was caged."),
    # Alpha Wolf
    ("Alpha Wolf", "Wolf (Changed-enhanced)", None, "Horse-sized wolf — leader of the wolf pack",
     "Dead — killed by Ketric's nat-20 critical hit",
     None,
     "Enemy — dead.",
     1, 1,
     "Horse-sized, grey/black, amber eyes. Spoke one word ('Come'). Slept among human bones. Killed by Ketric's nat-20 crit for 20 damage.",
     "Horse-sized, grey/black fur, amber eyes.",
     "Aggressive, supernatural. Spoke one word.",
     None, None),
    # Cobb Alderman
    ("Cobb Alderman", "Human", None, "Hunter — first to go missing",
     "Missing — fate unknown. Not in the cellar cage.",
     None,
     "Missing person — Nassa aware of his disappearance.",
     1, 1,
     "First missing, 3 weeks before Session 1. Not found in the cellar. Fate unknown — Changed recruit? Dead? Something else?",
     None, None,
     None, "Unknown — was hunting before disappearing."),
    # The Rescued Druid
    ("The Rescued Druid", "Wood Elf", "Druid (Emerald Enclave)", "Ally-in-waiting",
     "Alive, location unknown",
     None,
     "Deeply indebted to Nassa — saved by Nassa's squad from a goblin raiding party. Can provide herbal medicines, potions, or safe passage through magical woods.",
     0, 0,
     "Nassa deliberately never learned her name — but would recognize her anywhere. Perfect chance encounter hook at a critical moment.",
     "Wood elf. Nassa would recognize her anywhere.",
     "Deeply indebted. Grateful.",
     None, "Unknown — wandering druid of the Emerald Enclave."),
    # Therion
    ("Therion", "Presumably elven", None, "Wildwood Warden scout from ~15 years ago",
     "Unknown",
     None,
     "None — Nassa knows of Therion through Warden intel.",
     0, 0,
     "Filed intel on the Changed — skin-walkers who choose to shift. If still alive, knows more than anyone about the Changed.",
     None, None,
     None, "Unknown — filed the Warden report 15 years ago."),
]

cur.executemany("""
    INSERT INTO npcs (name, race, class, role, status, location, relationship,
        first_appearance_session, last_seen_session, notes, appearance,
        personality, equipment, motivation)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", npcs)

# ─── LOCATIONS ───
locations = [
    ("Thornhaven", "Borderlands", "Town",
     "Frontier town 2 hours south of Vaelthyr's well. In the danger zone if the well inverts. Has a gate with guards, the Hare & Hound inn, Madam Olara's herbalist shop.",
     1, "Base of operations for Session 1. Cobb Alderman and 2 hunters missing from here."),
    ("Vaelthyr's Well", "North of Thornhaven (~2 hrs)", "Ancient prison",
     "Fey lord Vaelthyr bound beneath the well. Wards in pre-Elvish geometric patterns. Covenantal binding requires a living keeper's blood. When the seal breaks, the well inverts — pulls everything nearby into itself.",
     1, "Discovered in Session 1. Nassa understood the full nature via natural-20 Religion check."),
    ("Warden Waystation", "South of Thornhaven", "Safe house",
     "Occupied, door marked 'Come in peace or don't come at all'. Currently the decision point — enter or move on.",
     1, "Where Nassa and Pras are at the end of Session 1."),
    ("Elven Homelands", "Unknown", "Home",
     "Nassa's origin. The Wildwood Wardens are based here. Nassa deeply misses the food, the smell of the woods, friends and family.",
     0, "Backstory location — not yet visited in play."),
]
cur.executemany("""
    INSERT INTO locations (name, region, type, description, discovered_session, notes)
    VALUES (?, ?, ?, ?, ?, ?)
""", locations)

# ─── FACTIONS ───
factions = [
    ("Wildwood Wardens", "Elvish military-monastic order",
     "Protect elven homelands through stealth, speed, and hand-to-hand combat. Intercept threats before they reach elven cities.",
     "Former member",
     "Trained Nassa as a monk. Waystation suggests active presence in the region. Filed intel on the Changed ~15 years ago (Therion)."),
    ("Green-Leaf Sentinels", "Elite scouting unit within the Wildwood Wardens",
     "Scouting and intelligence gathering.",
     "Former member",
     "Nassa's formal scouting unit. A handful of living members scattered across the world. They will always buy Nassa a drink, share military intelligence, or patch them up."),
    ("Emerald Enclave", "Nature-focused organization",
     "Nature preservation and protection.",
     "Ally / former scout",
     "Nassa worked as a scout for the Emerald Enclave. The Rescued Druid is a key contact — deeply indebted to Nassa."),
]
cur.executemany("""
    INSERT INTO factions (name, alignment, goals, standing_with_nassa, notes)
    VALUES (?, ?, ?, ?, ?)
""", factions)

# ─── PLOT THREADS ───
plot_threads = [
    ("Vaelthyr's Binding", "active", "red",
     "Full moon Day 6 (~3 days remaining). Three paths: Renew (blood + old words, requires keeper's cooperation), Break (destroy wards — catastrophic release, well inverts, Thornhaven destroyed), Face (go down into the well — direct confrontation with ancient Fey lord).",
     1, None,
     "Ticking clock. Full moon Day 6 is the likely deadline before the seal fails entirely."),
    ("Waystation Decision", "active", "red",
     "Right now. Occupied waystation, door marked 'Come in peace or don't come at all'. Pras with Nassa. Enter or move on?",
     1, None,
     "Immediate decision point at end of Session 1."),
    ("The Keeper", "dormant", "yellow",
     "Who is the Keeper? Are they still alive? Where are they? The binding requires their blood to maintain.",
     1, None,
     "Key to the Renew path for Vaelthyr's binding."),
    ("The Changed", "dormant", "yellow",
     "The Changed Leader escaped. Cellar guard had a geometric brand — does it connect to Vaelthyr's wards? Dwarven oral tradition (Ketric knows more). Warden intel from Therion, 15 years old. What happened to Therion?",
     1, None,
     "Not lycanthropes — they choose to shift, wear skins like clothes. Ketric calls them by an older dwarvish name."),
    ("Missing Hunters", "dormant", "yellow",
     "Cobb Alderman + 2 other hunters. Not in the cellar. Still out there. Changed recruits? Dead? Something else?",
     1, None,
     "Cobb was first missing, 3 weeks ago. Two hunters sent after him also never returned."),
    ("Ketric & Vera", "dormant", "yellow",
     "Still in Thornhaven. Ketric 'had something to do.' Vera holding his 16 gp. Will they cross paths with Nassa again?",
     1, None,
     "Potential allies for the Vaelthyr mission if Nassa returns to Thornhaven."),
    ("Corra's Debt", "dormant", "yellow",
     "Iron pitons and silver chain were a contract to bring Pras back. Pras is alive and with Nassa. Corra doesn't know. Returning to Thornhaven means facing that.",
     1, None,
     "Nassa still carries the pitons and chain. Pras is alive — the contract can be fulfilled."),
    ("Lost Comrades", "dormant", "yellow",
     "Green-Leaf Sentinels scattered across the world. Names TBD.",
     0, None,
     "Backstory thread — former unit members who could resurface."),
    ("Rescued Druid", "dormant", "yellow",
     "Out there somewhere. Nameless, indebted, waiting. Perfect chance encounter at a critical moment.",
     0, None,
     "Nassa never learned her name but would recognize her anywhere. Can provide herbal medicines, potions, or safe passage through magical woods."),
    ("Nassa's Departure", "dormant", "yellow",
     "Why did Nassa really leave the Wardens? 'Seeking knowledge' feels like a polite answer for something deeper.",
     0, None,
     "Character backstory mystery — the real reason Nassa left the elven homelands."),
    ("What is the Wildwood Echo?", "dormant", "yellow",
     "A place? An event? A prophecy? The name of the binding itself? The campaign's central mystery.",
     0, None,
     "Meta-plot question — the meaning of the campaign name in-world."),
]
cur.executemany("""
    INSERT INTO plot_threads (title, status, priority, description, opened_session,
        resolved_session, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", plot_threads)

# ─── SESSION EVENTS (Session 1) ───
events = [
    (session1_id, 1, "social",
     "Nassa arrives in Thornhaven; meets Ketric Bronzebeard (dwarf fighter) and Vera (human ranger) at the Hare & Hound. Marta (barkeep) gives Nassa the local rate; Vera vouches.",
     None, "Party formed: Nassa, Ketric, Vera."),
    (session1_id, 2, "social",
     "Patchy Beard (gate guard) recognizes the Wildwood Wardens by reputation; tests Nassa's background. Younger guard curious about Wardens fighting bare-handed.",
     None, "Entry to Thornhaven granted with soldier's respect."),
    (session1_id, 3, "exploration",
     "Investigate the wolf threat — Changed skin-walkers operating from the old watchtower. Track to the watchtower.",
     None, "Mission accepted: investigate wolf attacks and missing patrol."),
    (session1_id, 4, "combat",
     "Watchtower cellar: Cellar guard killed by Ketric. Wore wolf-claw talisman, branded wrist with geometric symbol (Changed mark).",
     "Ketric melee kills cellar guard",
     "Cellar guard dead. Geometric brand discovered — possible connection to Vaelthyr's wards."),
    (session1_id, 5, "discovery",
     "Pras found alive in an iron cage in the cellar. Bought time so Corra and Fen could escape. Voice destroyed from captivity.",
     None, "Pras rescued. Corra's contract can be fulfilled."),
    (session1_id, 6, "combat",
     "Alpha wolf (horse-sized, grey/black, amber eyes, spoke 'Come') killed by Ketric's nat-20 critical hit for 20 damage.",
     "Ketric nat-20 crit, 20 damage",
     "Alpha wolf dead. Changed Leader escaped — unaccounted for."),
    (session1_id, 7, "social",
     "Corra gives Nassa iron pitons + silver chain — a contract to bring Pras back. Genuine grief. Fen won't talk about what happened.",
     None, "Contract accepted. Nassa carries the pitons and chain."),
    (session1_id, 8, "discovery",
     "Cobb Alderman + 2 hunters still missing — not in the cellar. Fate unknown.",
     None, "Mystery deepens — 3 people still unaccounted for."),
    (session1_id, 9, "exploration",
     "Nassa investigates strange occurrences — led to the well north of town. Wolf encounter near the well — Nassa bitten, poisoned; recovered with Madam Olara's treatment.",
     None, "Nassa wounded then healed. Acquired healing potions and healer's kit from Madam Olara."),
    (session1_id, 10, "lore",
     "Religion check (natural 20): Nassa fully understood Vaelthyr's prison — the covenant, the keeper, the binding, the inversion, the deadline.",
     "Nassa nat-20 Religion check",
     "Full understanding of Vaelthyr's binding. Three paths revealed: renew, break, or face directly. Full moon Day 6 is the deadline."),
    (session1_id, 11, "decision",
     "Three paths: Renew (blood + old words), Break (destroy wards — catastrophic), Face (go down into the well). Decision deferred.",
     None, "Nassa must choose a path before the full moon on Day 6."),
    (session1_id, 12, "exploration",
     "Travel south with Pras to the Warden waystation. Pras paid 5 GP for aid.",
     None, "Nassa and Pras at the waystation door. Ketric & Vera remain in Thornhaven."),
    (session1_id, 13, "decision",
     "At the waystation door — occupied, marked 'Come in peace or don't come at all'. Enter or move on?",
     None, "Cliffhanger — session ends at the decision point."),
]
cur.executemany("""
    INSERT INTO session_events (session_id, event_order, event_type, description,
        dice_rolls, consequences)
    VALUES (?, ?, ?, ?, ?, ?)
""", events)

# ─── COMBAT LOG (Session 1) ───
combat = [
    (session1_id, "Cellar Guard (human Changed follower)",
     "Victory — guard killed by Ketric",
     "Ketric melee kills",
     0, None,  # damage_taken/dealt unknown for Nassa specifically
     "Guard wore wolf-claw talisman, branded wrist with geometric symbol (Changed mark). Vera stealth-takedowned initially, Ketric finished in combat."),
    (session1_id, "Alpha Wolf (horse-sized, Changed-enhanced)",
     "Victory — alpha wolf killed by Ketric's nat-20 critical hit",
     "Ketric nat-20 crit, 20 damage",
     None, 20,  # 20 damage dealt by Ketric's crit
     "Horse-sized, grey/black, amber eyes. Spoke one word ('Come'). Slept among human bones. Changed Leader escaped after the alpha died."),
]
cur.executemany("""
    INSERT INTO combat_log (session_id, enemy, outcome, notable_rolls,
        damage_taken, damage_dealt, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", combat)

# ─── WORLD STATE ───
world_state = [
    ("current_in_world_day", "3", "Day 3 of the campaign"),
    ("in_world_time", "late afternoon", "~2 hours of daylight remain"),
    ("full_moon_day", "6", "Full moon — likely deadline for Vaelthyr's seal"),
    ("days_remaining_to_full_moon", "3", "~3 days until the seal fails entirely"),
    ("current_location", "Warden waystation, south of Thornhaven", "Nassa and Pras at the waystation door"),
    ("vaelthyr_binding_status", "fraying", "The binding is fraying. Full moon Day 6 is the likely deadline."),
    ("changed_leader_status", "escaped", "The Changed Leader escaped after the alpha wolf was killed. Unaccounted for."),
    ("cobb_alderman_status", "missing", "Cobb Alderman + 2 hunters still missing. Not in the cellar."),
    ("pras_status", "with_nassa", "Pras is alive and with Nassa at the waystation. Paid 5 GP."),
    ("ketric_status", "in_thornhaven", "Ketric left after the watchtower mission — 'had something to do.' Vera holding 16 gp."),
    ("vera_status", "in_thornhaven", "Vera at the Hare & Hound. Holding Ketric's 16 gp."),
    ("corra_debt", "open", "Corra's contract to bring Pras back is still open. Corra doesn't know Pras is alive."),
]
cur.executemany("""
    INSERT INTO world_state (key, value, notes)
    VALUES (?, ?, ?)
""", world_state)

conn.commit()
conn.close()
print(f"Database created at {DB_PATH}")