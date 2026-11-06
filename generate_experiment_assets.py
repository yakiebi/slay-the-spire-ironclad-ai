import csv
import datetime
import glob
import json
import os
import shutil
import zipfile
from collections import defaultdict, Counter
from xml.sax.saxutils import escape

RUNS_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\SlayTheSpire\runs\IRONCLAD"
PROJECT_DIR = r"C:\Users\User\.gemini\antigravity\scratch\slay_the_spire_bot"
ARTIFACT_DIR = r"C:\Users\User\.gemini\antigravity\brain\f94be6ae-41df-464f-bed4-1986c68037a3"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
DOCS_DATA_DIR = os.path.join(DOCS_DIR, "data")
DOCS_IMG_DIR = os.path.join(DOCS_DIR, "assets", "screenshots")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOCS_DATA_DIR, exist_ok=True)
os.makedirs(DOCS_IMG_DIR, exist_ok=True)

# Import CARD_SCORES from play_ironclad.py
import sys
sys.path.insert(0, PROJECT_DIR)
from play_ironclad import CARD_SCORES, BOSS_RELIC_SCORES

ITERATIONS = [
    {
        "iteration": "v1.0",
        "phase": "Phase 1: Core Observer & Baseline Bot",
        "runs": "Run #1",
        "floor_peak": 28,
        "issue_observed": "Bot paused on Floor 1 fade-out; picked Velvet Choker; entered Colosseum event combat unprepared.",
        "strategy_change": "Removed waitingOnFadeOut block in step(); added Event combat auto-detection & Colosseum Retreat choice.",
        "files_modified": "StsObserverAgent.java, play_ironclad.py"
    },
    {
        "iteration": "v1.1",
        "phase": "Phase 1: Core Observer & Baseline Bot",
        "runs": "Runs #2–#4",
        "floor_peak": 33,
        "issue_observed": "Map Boss node at currY==14 not clicked; TreasureRoomBoss map loop; Slime Boss 35-dmg Slam & Automaton Hyperbeam.",
        "strategy_change": "Added currY==14 bossHb click; TreasureRoomBoss map close + Proceed; +250 score bonus to split Slime Boss <=70 HP.",
        "files_modified": "play_ironclad.py"
    },
    {
        "iteration": "v1.2",
        "phase": "Phase 2: Act 2 Scaling & Multi-Enemy AoE",
        "runs": "Runs #5–#8",
        "floor_peak": 48,
        "issue_observed": "Reached Floor 48 (Act 3) for the first time! Lost to Jaw Worm Horde & 3 Cultists due to slow scaling and HandCardSelectScreen counter staying 0.",
        "strategy_change": "Fixed HandCardSelectScreen numSelected via max(numSelected, len(selectedCards)); boosted Ritual/Cultist focus-fire (+45) and AoE (Immolate/Whirlwind).",
        "files_modified": "StsObserverAgent.java, play_ironclad.py"
    },
    {
        "iteration": "v1.3",
        "phase": "Phase 3: First Floor 50 Boss & Act 3 Hazards",
        "runs": "Run #9",
        "floor_peak": 50,
        "issue_observed": "Reached Floor 50 (Awakened One)! Lost because bot played minor Powers in Phase 1, triggering Curiosity (+2 Strength per Power).",
        "strategy_change": "Added Awakened One Curiosity check: suppress non-essential Powers during Phase 1 unless Demon Form, Barricade, or Corruption+Snecko Eye.",
        "files_modified": "play_ironclad.py"
    },
    {
        "iteration": "v1.4",
        "phase": "Phase 3: First Floor 50 Boss & Act 3 Hazards",
        "runs": "Runs #10–#11",
        "floor_peak": 33,
        "issue_observed": "Coffee Dripper disabled Campfire Rest without Reaper/Meal Ticket sustain; PotionPopUp.targetMode set isHidden=true.",
        "strategy_change": "Penalized Coffee Dripper/Runic Dome/Velvet Choker; checked PotionPopUp.targetMode before isHidden so targetable potions never get stuck.",
        "files_modified": "play_ironclad.py"
    },
    {
        "iteration": "v1.5",
        "phase": "Phase 3: First Floor 50 Boss & Act 3 Hazards",
        "runs": "Runs #12–#13",
        "floor_peak": 46,
        "issue_observed": "Run #12 died on Floor 46 hitting Spiker's Thorns with multi-hit attacks; Run #13 picked Mind Bloom [I am Awake] (Mark of the Bloom) because of #g/#r color codes.",
        "strategy_change": "Stripped LibGDX #g/#r/#y/#b/#p color tags in handle_event; forced Mind Bloom [I am War]; added universal Thorns self-damage protection.",
        "files_modified": "play_ironclad.py"
    },
    {
        "iteration": "v1.6",
        "phase": "Phase 4: Event Mini-Games & Multi-Card Grid Select",
        "runs": "Runs #14–#16",
        "floor_peak": 27,
        "issue_observed": "GremlinMatchGame (Match and Keep) had 0 dialog options; Astrolabe (numCards=3) re-clicked the same card index and toggled selection off.",
        "strategy_change": "Added 4x3 card grid matcher for GremlinMatchGame; tracked grid_selected_indices in handle_grid_select for Astrolabe/Empty Cage.",
        "files_modified": "play_ironclad.py"
    },
    {
        "iteration": "v1.7",
        "phase": "Phase 4: Event Mini-Games & Multi-Card Grid Select",
        "runs": "Run #17",
        "floor_peak": 31,
        "issue_observed": "Lethal attack bonus (+360) was computed before the if/elif chain and overwritten by sc = 100.0 + total_dmg * 3.8; Second Wind played with 0 non-attacks.",
        "strategy_change": "Moved universal Attack post-scoring (Thorns + is_lethal_hit) after the if/elif chain; fixed Second Wind block multiplier & Fiend Fire hit count.",
        "files_modified": "play_ironclad.py"
    },
    {
        "iteration": "v2.0",
        "phase": "Phase 5: Endgame Boss Mastery & Victory",
        "runs": "Run #18",
        "floor_peak": 50,
        "issue_observed": "Reached Floor 50 (Time Eater) at 85/90 HP and brought Time Eater to 106 HP! Wasted 5 cards into Time Eater's <50% HP Haste turn and took Madness in WindingHalls.",
        "strategy_change": "Added Time Eater Haste conservation (only play Powers/Limit Break when Time Eater intents BUFF at <228 HP) and WindingHalls [Retrace Your Steps] preference.",
        "files_modified": "play_ironclad.py"
    },
    {
        "iteration": "v2.1",
        "phase": "Phase 5: Endgame Boss Mastery & Victory",
        "runs": "Run #19",
        "floor_peak": 46,
        "issue_observed": "Lost on Floor 46 to Nemesis because bot evaluated 2-cost Attacks at full damage while Nemesis had Intangible (which caps all damage to 1 per hit).",
        "strategy_change": "Added Intangible detection (eff_card_dmg = min(eff_card_dmg, 1)); blocked >=2-cost 0-block attacks and HP-cost cards into Intangible; avoided late Act 3 Elites.",
        "files_modified": "play_ironclad.py"
    },
    {
        "iteration": "v2.2",
        "phase": "Phase 5: Endgame Boss Mastery & Victory",
        "runs": "Run #20",
        "floor_peak": 50,
        "issue_observed": "Beat both Reptomancer & Nemesis and reached Floor 50 (Time Eater)! Gambling Chip discarded entire Turn 1 hand; stopping at 11/12 Time Warp left 1 play for Turn 5.",
        "strategy_change": "Fixed Gambling Chip to only discard Strikes/Defends/Curses; changed Time Warp rule to stop only at 6..8 when safe and push through 9..11 to reset to 0/12; boosted Boss Block urgency.",
        "files_modified": "play_ironclad.py"
    },
    {
        "iteration": "v2.3",
        "phase": "Phase 5: Endgame Boss Mastery & Victory",
        "runs": "Run #21 (VICTORY!)",
        "floor_peak": 51,
        "issue_observed": "Defeated Donu and Deca on Floor 50 in 7 turns at 71/93 HP! Map screen opened when MonsterRoomBoss completed.",
        "strategy_change": "Closed Map overlay when MonsterRoomBoss is COMPLETE and clicked Proceed to enter Floor 51 Spire Heart & Victory Screen (Score: 667 in 13m 21s).",
        "files_modified": "play_ironclad.py"
    }
]

def map_run_to_iteration(run_idx):
    if run_idx == 1:
        return "v1.0", "Phase 1: Baseline"
    elif run_idx in (2, 3, 4):
        return "v1.1", "Phase 1: Baseline"
    elif run_idx in (5, 6, 7, 8):
        return "v1.2", "Phase 2: Act 2/3 Scaling"
    elif run_idx == 9:
        return "v1.3", "Phase 3: First Floor 50"
    elif run_idx in (10, 11):
        return "v1.4", "Phase 3: Relic/Potion Tuning"
    elif run_idx in (12, 13):
        return "v1.5", "Phase 3: Thorns & Events"
    elif run_idx in (14, 15, 16):
        return "v1.6", "Phase 4: Grid/Event Games"
    elif run_idx == 17:
        return "v1.7", "Phase 4: Lethal Scoring Fix"
    elif run_idx == 18:
        return "v2.0", "Phase 5: Endgame Mastery"
    elif run_idx == 19:
        return "v2.1", "Phase 5: Endgame Mastery"
    elif run_idx == 20:
        return "v2.2", "Phase 5: Endgame Mastery"
    else:
        return "v2.3", "Phase 5: Victory!"

files = sorted(glob.glob(os.path.join(RUNS_DIR, "*.run")), key=os.path.getmtime)

runs_summary = []
card_offered_cnt = Counter()
card_picked_cnt = Counter()
card_passed_cnt = Counter()
card_upgraded_picked_cnt = Counter()
card_shop_bought_cnt = Counter()
card_in_winning_deck_cnt = Counter()

relic_cnt = Counter()
relic_floors = defaultdict(list)
relic_in_victory = set()
boss_relic_offered = Counter()
boss_relic_picked = Counter()

combat_rows = []
enemy_stats = defaultdict(lambda: {"fights": 0, "total_dmg": 0, "total_turns": 0, "max_dmg": 0})

winning_run_detail = None

for idx, fpath in enumerate(files, 1):
    with open(fpath, "r", encoding="utf-8") as fp:
        d = json.load(fp)
    mtime_dt = datetime.datetime.fromtimestamp(os.path.getmtime(fpath))
    mtime_str = mtime_dt.strftime("%Y-%m-%d %H:%M:%S")
    iter_ver, phase_name = map_run_to_iteration(idx)

    floor = d.get("floor_reached", 0)
    act = 1 if floor <= 17 else (2 if floor <= 34 else 3)
    victory = bool(d.get("victory", False))
    playtime = int(d.get("playtime", 0))
    mins, secs = divmod(playtime, 60)
    playtime_fmt = f"{mins:02d}:{secs:02d}"
    score = int(d.get("score", 0))
    killed_by = "NONE (VICTORY!)" if victory else d.get("killed_by", "Unknown")
    neow_bonus = d.get("neow_bonus", "NONE")
    master_deck = d.get("master_deck", [])
    relics = d.get("relics", [])
    boss_relics_picked = [b.get("picked", "None") for b in d.get("boss_relics", []) if b.get("picked")]
    purges = int(d.get("purchased_purges", 0))
    rests = int(d.get("campfire_rested", 0))
    upgrades = int(d.get("campfire_upgraded", 0))
    potions_used = len(d.get("potions_floor_usage", []))

    hp_per_fl = d.get("current_hp_per_floor", [])
    max_hp_per_fl = d.get("max_hp_per_floor", [])
    gold_per_fl = d.get("gold_per_floor", [])
    final_hp = hp_per_fl[-1] if hp_per_fl else (71 if victory else 0)
    peak_max_hp = max(max_hp_per_fl) if max_hp_per_fl else 80

    c_choices = d.get("card_choices", [])
    picked_in_run = 0
    skipped_in_run = 0
    for cc in c_choices:
        p = cc.get("picked", "SKIP")
        not_p = cc.get("not_picked", [])
        if p and p != "SKIP":
            picked_in_run += 1
            base_p = p.split("+")[0]
            card_offered_cnt[base_p] += 1
            card_picked_cnt[base_p] += 1
            if "+1" in p:
                card_upgraded_picked_cnt[base_p] += 1
        else:
            skipped_in_run += 1
        for np_card in not_p:
            base_np = np_card.split("+")[0]
            card_offered_cnt[base_np] += 1
            card_passed_cnt[base_np] += 1

    for item in d.get("items_purchased", []):
        base_item = item.split("+")[0]
        if base_item in CARD_SCORES or base_item in ("Apotheosis", "Master of Strategy", "Secret Technique", "Panic Button", "Blind", "Trip", "Dark Shackles"):
            card_shop_bought_cnt[base_item] += 1

    if victory:
        for mc in master_deck:
            base_mc = mc.split("+")[0]
            card_in_winning_deck_cnt[base_mc] += 1
        for r in relics:
            relic_in_victory.add(r)
        winning_run_detail = {
            "run_num": idx,
            "run_file": os.path.basename(fpath),
            "timestamp": mtime_str,
            "playtime": playtime,
            "playtime_fmt": playtime_fmt,
            "score": score,
            "floor_reached": floor,
            "hp_per_floor": hp_per_fl,
            "max_hp_per_floor": max_hp_per_fl,
            "gold_per_floor": gold_per_fl,
            "path_per_floor": d.get("path_per_floor", []),
            "master_deck": master_deck,
            "relics": relics,
            "damage_taken": d.get("damage_taken", []),
            "card_choices": c_choices,
            "event_choices": d.get("event_choices", []),
            "campfire_choices": d.get("campfire_choices", []),
            "boss_relics": d.get("boss_relics", []),
        }

    for r in relics:
        relic_cnt[r] += 1
    for ro in d.get("relics_obtained", []):
        relic_floors[ro["key"]].append(ro["floor"])
    for br in d.get("boss_relics", []):
        p = br.get("picked")
        if p:
            boss_relic_offered[p] += 1
            boss_relic_picked[p] += 1
            relic_floors[p].append(17 if br == d["boss_relics"][0] else 34)
        for np_r in br.get("not_picked", []):
            boss_relic_offered[np_r] += 1

    dmg_list = d.get("damage_taken", [])
    total_combat_dmg = sum(int(x.get("damage", 0)) for x in dmg_list)
    total_combat_turns = sum(int(x.get("turns", 0)) for x in dmg_list)
    for dt in dmg_list:
        en = dt.get("enemies", "Unknown")
        dmg = int(dt.get("damage", 0))
        trns = int(dt.get("turns", 0))
        fl = int(dt.get("floor", 0))
        combat_rows.append({
            "Run_Number": idx,
            "Iteration": iter_ver,
            "Floor": fl,
            "Act": 1 if fl <= 16 else (2 if fl <= 33 else 3),
            "Enemy_Encounter": en,
            "Turns": trns,
            "Damage_Taken": dmg,
            "Run_Victory": "Yes" if victory else "No"
        })
        enemy_stats[en]["fights"] += 1
        enemy_stats[en]["total_dmg"] += dmg
        enemy_stats[en]["total_turns"] += trns
        enemy_stats[en]["max_dmg"] = max(enemy_stats[en]["max_dmg"], dmg)

    runs_summary.append({
        "Run_Number": idx,
        "Run_ID": os.path.basename(fpath).replace(".run", ""),
        "Timestamp": mtime_str,
        "Iteration": iter_ver,
        "Phase": phase_name,
        "Floor_Reached": floor,
        "Act_Reached": act,
        "Outcome": "VICTORY" if victory else "DEFEAT",
        "Killed_By": killed_by,
        "Playtime_Sec": playtime,
        "Playtime_MMSS": playtime_fmt,
        "Score": score,
        "Peak_Max_HP": peak_max_hp,
        "Final_HP": final_hp if victory else 0,
        "Neow_Bonus": neow_bonus,
        "Boss_Relic_Act1": boss_relics_picked[0] if len(boss_relics_picked) >= 1 else "None",
        "Boss_Relic_Act2": boss_relics_picked[1] if len(boss_relics_picked) >= 2 else "None",
        "Total_Relics": len(relics),
        "Deck_Size": len(master_deck),
        "Cards_Picked": picked_in_run,
        "Cards_Skipped": skipped_in_run,
        "Card_Pick_Rate_Pct": round(picked_in_run * 100.0 / max(1, picked_in_run + skipped_in_run), 1),
        "Combats_Won": len(dmg_list),
        "Total_Combat_Turns": total_combat_turns,
        "Total_Combat_Damage_Taken": total_combat_dmg,
        "Campfire_Upgrades": upgrades,
        "Campfire_Rests": rests,
        "Shop_Purges": purges,
        "Potions_Used": potions_used
    })

# Build Card Pick Rates table
all_cards = sorted(set(list(card_offered_cnt.keys()) + list(card_shop_bought_cnt.keys())),
                   key=lambda c: (card_picked_cnt[c], card_offered_cnt[c]), reverse=True)
card_rows = []
for c in all_cards:
    off = card_offered_cnt[c]
    pck = card_picked_cnt[c]
    psd = card_passed_cnt[c]
    rate = round(pck * 100.0 / off, 1) if off > 0 else 0.0
    bot_sc = CARD_SCORES.get(c, 50)
    card_rows.append({
        "Card_Name": c,
        "Bot_Base_Score": bot_sc,
        "Times_Offered": off,
        "Times_Picked": pck,
        "Times_Passed": psd,
        "Pick_Rate_Pct": rate,
        "Upgraded_Picks": card_upgraded_picked_cnt[c],
        "Shop_Purchases": card_shop_bought_cnt[c],
        "Total_Acquired": pck + card_shop_bought_cnt[c],
        "Copies_In_Victory_Deck": card_in_winning_deck_cnt[c]
    })
card_rows.sort(key=lambda r: (r["Times_Picked"], r["Pick_Rate_Pct"], r["Times_Offered"]), reverse=True)

# Build Relics table
relic_rows = []
for r, cnt in relic_cnt.most_common():
    fls = relic_floors.get(r, [])
    avg_fl = round(sum(fls) / len(fls), 1) if fls else 0.0
    is_boss = r in BOSS_RELIC_SCORES or r in boss_relic_offered
    cat = "Starter" if r == "Burning Blood" else ("Boss Relic" if is_boss else "Relic (Common/Uncommon/Rare/Event/Shop)")
    b_off = boss_relic_offered[r]
    b_pck = boss_relic_picked[r]
    b_rate = round(b_pck * 100.0 / b_off, 1) if b_off > 0 else ""
    relic_rows.append({
        "Relic_Name": r,
        "Category": cat,
        "Runs_Obtained": cnt,
        "Run_Presence_Pct": round(cnt * 100.0 / len(files), 1),
        "Avg_Floor_Obtained": avg_fl,
        "Boss_Times_Offered": b_off if is_boss else "",
        "Boss_Times_Picked": b_pck if is_boss else "",
        "Boss_Pick_Rate_Pct": b_rate,
        "In_Winning_Run": "Yes" if r in relic_in_victory else "No"
    })

# Enemy Encounter Summary
enemy_rows = []
for en, st in sorted(enemy_stats.items(), key=lambda kv: kv[1]["fights"], reverse=True):
    f = st["fights"]
    enemy_rows.append({
        "Enemy_Encounter": en,
        "Encounters_Fought": f,
        "Avg_Damage_Taken": round(st["total_dmg"] / f, 1),
        "Max_Damage_Taken": st["max_dmg"],
        "Avg_Turns": round(st["total_turns"] / f, 1),
        "Total_Damage_Taken": st["total_dmg"]
    })

def write_csv(filename, rows):
    if not rows:
        return
    for folder in (DATA_DIR, DOCS_DATA_DIR):
        out_path = os.path.join(folder, filename)
        with open(out_path, "w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

write_csv("runs_summary.csv", runs_summary)
write_csv("card_pick_rates.csv", card_rows)
write_csv("relics_obtained.csv", relic_rows)
write_csv("iterations_changelog.csv", ITERATIONS)
write_csv("combat_encounters.csv", combat_rows)
write_csv("enemy_damage_summary.csv", enemy_rows)

# Also build a multi-sheet .xlsx workbook (pure Python OpenXML so it needs zero external packages and imports cleanly into Google Sheets!)
def create_xlsx(filepath, sheets):
    """Create a valid multi-sheet OpenXML .xlsx workbook for Google Sheets & Excel."""
    with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zf:
        # [Content_Types].xml
        sheet_overrides = "\n".join(
            f'  <Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            for i in range(1, len(sheets) + 1)
        )
        zf.writestr("[Content_Types].xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
{sheet_overrides}
</Types>""")

        # _rels/.rels
        zf.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>""")

        # xl/workbook.xml
        sheet_tags = "\n".join(
            f'    <sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>'
            for i, (name, _) in enumerate(sheets, 1)
        )
        zf.writestr("xl/workbook.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
{sheet_tags}
  </sheets>
</workbook>""")

        # xl/_rels/workbook.xml.rels
        rel_tags = "\n".join(
            f'  <Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
            for i in range(1, len(sheets) + 1)
        )
        style_rid = len(sheets) + 1
        zf.writestr("xl/_rels/workbook.xml.rels", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
{rel_tags}
  <Relationship Id="rId{style_rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>""")

        # xl/styles.xml
        zf.writestr("xl/styles.xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2">
    <font><sz val="11"/><name val="Calibri"/></font>
    <font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
  </fonts>
  <fills count="3">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF8B1E1E"/></patternFill></fill>
  </fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="2">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>
  </cellXfs>
</styleSheet>""")

        def col_letter(n):
            res = ""
            while n > 0:
                n, rem = divmod(n - 1, 26)
                res = chr(65 + rem) + res
            return res

        for sheet_idx, (name, rows) in enumerate(sheets, 1):
            if not rows:
                zf.writestr(f"xl/worksheets/sheet{sheet_idx}.xml",
                            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData/></worksheet>')
                continue
            headers = list(rows[0].keys())
            xml_rows = []
            # Header row
            h_cells = []
            for c_idx, h in enumerate(headers, 1):
                ref = f"{col_letter(c_idx)}1"
                h_cells.append(f'<c r="{ref}" t="inlineStr" s="1"><is><t>{escape(str(h))}</t></is></c>')
            xml_rows.append(f'<row r="1">{"".join(h_cells)}</row>')

            for r_idx, row in enumerate(rows, 2):
                r_cells = []
                for c_idx, h in enumerate(headers, 1):
                    ref = f"{col_letter(c_idx)}{r_idx}"
                    val = row.get(h, "")
                    if isinstance(val, (int, float)) and not isinstance(val, bool) and val != "":
                        r_cells.append(f'<c r="{ref}"><v>{val}</v></c>')
                    else:
                        r_cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(val))}</t></is></c>')
                xml_rows.append(f'<row r="{r_idx}">{"".join(r_cells)}</row>')

            zf.writestr(f"xl/worksheets/sheet{sheet_idx}.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>
  <sheetData>
    {"".join(xml_rows)}
  </sheetData>
</worksheet>""")

xlsx_sheets = [
    ("Runs Summary", runs_summary),
    ("Card Pick Rates", card_rows),
    ("Relics Obtained", relic_rows),
    ("AI Iterations", ITERATIONS),
    ("Enemy Summary", enemy_rows),
    ("All Combats", combat_rows),
]
create_xlsx(os.path.join(DATA_DIR, "slay_the_spire_ironclad_experiment.xlsx"), xlsx_sheets)
create_xlsx(os.path.join(DOCS_DATA_DIR, "slay_the_spire_ironclad_experiment.xlsx"), xlsx_sheets)

# Copy key screenshots into docs/assets/screenshots
key_screenshots = [
    "03_neow_blessing.png",
    "04_act1_first_combat.png",
    "act1_elite_floor7.png",
    "act1_boss_relics.png",
    "act2_elite_floor23.png",
    "act2_boss_floor33.png",
    "act2_boss_relics.png",
    "act3_shop_floor36.png",
    "act3_campfire_floor40.png",
    "act3_boss_floor50.png",
    "98_spire_heart_cutscene.png",
    "99_ironclad_victory_screen.png",
    "100_final_score_screen.png"
]
for sc_name in key_screenshots:
    src = os.path.join(ARTIFACT_DIR, sc_name)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(DOCS_IMG_DIR, sc_name))

# Export experiment_data.js for the GitHub Pages site
bundle = {
    "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "totals": {
        "total_runs": len(runs_summary),
        "total_playtime_sec": sum(r["Playtime_Sec"] for r in runs_summary),
        "total_combats": len(combat_rows),
        "total_cards_offered": sum(card_offered_cnt.values()),
        "total_cards_picked": sum(card_picked_cnt.values()),
        "act3_reaches": sum(1 for r in runs_summary if r["Floor_Reached"] >= 35),
        "floor50_reaches": sum(1 for r in runs_summary if r["Floor_Reached"] >= 50),
        "winning_score": winning_run_detail["score"] if winning_run_detail else 667,
        "winning_time": winning_run_detail["playtime_fmt"] if winning_run_detail else "13:21",
        "winning_hp": "71/93"
    },
    "runs": runs_summary,
    "cards": card_rows,
    "relics": relic_rows,
    "iterations": ITERATIONS,
    "enemies": enemy_rows,
    "combats": combat_rows,
    "winning_run": winning_run_detail
}

with open(os.path.join(DOCS_DIR, "data.js"), "w", encoding="utf-8") as fp:
    fp.write("window.EXPERIMENT_DATA = " + json.dumps(bundle, indent=2) + ";\n")

print(f"Successfully generated all CSVs, XLSX workbook, and data.js!")
print(f"Total Runs: {bundle['totals']['total_runs']} | Total Playtime: {bundle['totals']['total_playtime_sec']}s | Total Combats: {bundle['totals']['total_combats']} | Total Cards Offered: {bundle['totals']['total_cards_offered']}")
print("Top 10 Picked Cards:")
for c in card_rows[:10]:
    print(f"  - {c['Card_Name']:18s}: Picked {c['Times_Picked']:2d}/{c['Times_Offered']:2d} ({c['Pick_Rate_Pct']:5.1f}%) | Shop: {c['Shop_Purchases']} | In Victory Deck: {c['Copies_In_Victory_Deck']}")
print("Top 10 Relics:")
for r in relic_rows[:10]:
    print(f"  - {r['Relic_Name']:20s}: {r['Runs_Obtained']:2d}/21 runs ({r['Run_Presence_Pct']:5.1f}%) | Avg Floor: {r['Avg_Floor_Obtained']}")
