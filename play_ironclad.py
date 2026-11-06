import urllib.request
import urllib.parse
import json
import time
import os
import sys
import re

BASE = "http://127.0.0.1:17575"
ART_DIR = "C:/Users/User/.gemini/antigravity/brain/f94be6ae-41df-464f-bed4-1986c68037a3"
LOG_FILE = "C:/Users/User/.gemini/antigravity/scratch/slay_the_spire_bot/run_history.log"

def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def get_state():
    for attempt in range(5):
        try:
            with urllib.request.urlopen(f"{BASE}/state", timeout=5) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            time.sleep(0.3)
    return {}

def click(x, y, wait=0.25):
    url = f"{BASE}/action?cmd=click&x={int(round(x))}&y={int(round(y))}"
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            res = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        res = {"ok": False, "error": str(e)}
    if wait > 0:
        time.sleep(wait)
    return res

def play_card_api(card_index, target_index=-1, wait=0.35):
    url = f"{BASE}/action?cmd=play_card&cardIndex={card_index}&targetIndex={target_index}"
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            res = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        res = {"ok": False, "error": str(e)}
    if wait > 0:
        time.sleep(wait)
    return res

def end_turn_api(wait=0.5):
    url = f"{BASE}/action?cmd=end_turn"
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            res = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        res = {"ok": False, "error": str(e)}
    if wait > 0:
        time.sleep(wait)
    return res

def hand_select_api(card_index, wait=0.25):
    url = f"{BASE}/action?cmd=hand_select&cardIndex={card_index}"
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            res = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        res = {"ok": False, "error": str(e)}
    if wait > 0:
        time.sleep(wait)
    return res

def scroll_api(direction="up", steps=5, wait=0.2):
    url = f"{BASE}/action?cmd=scroll&dir={direction}&steps={steps}"
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            res = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        res = {"ok": False, "error": str(e)}
    if wait > 0:
        time.sleep(wait)
    return res

def screenshot(name):
    path = f"{ART_DIR}/{name}"
    url = f"{BASE}/screenshot?path={urllib.parse.quote(path)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            res = json.loads(r.read().decode("utf-8"))
            log(f"Saved screenshot: {name}")
            return res
    except Exception as e:
        log(f"Screenshot error ({name}): {e}")
        return {"ok": False}

# Card Tier Scores for Ironclad Deckbuilding
CARD_SCORES = {
    # S-Tier / Core Winners
    "Bash": 78,
    "Offering": 98,
    "Immolate": 96,
    "Whirlwind": 92,
    "Feed": 90,
    "Reaper": 90,
    "Corruption": 88,
    "Feel No Pain": 87,
    "Shockwave": 88,
    "Impervious": 86,
    "Disarm": 85,
    "Battle Trance": 85,
    "Demon Form": 84,
    "Inflame": 82,
    "Spot Weakness": 81,
    "Uppercut": 80,
    "Shrug It Off": 79,
    "Flame Barrier": 78,
    "Limit Break": 77,
    "Fiend Fire": 82,
    "Barricade": 74,
    # A-Tier Frontload & Utility
    "Carnage": 76,
    "Hemokinesis": 75,
    "Blood for Blood": 74,
    "Pommel Strike": 73,
    "True Grit": 72,
    "Power Through": 73,
    "Metallicize": 72,
    "Clothesline": 70,
    "Twin Strike": 69,
    "Heavy Blade": 68,
    "Body Slam": 68,
    "Armaments": 67,
    "Ghostly Armor": 66,
    "Bludgeon": 74,
    "Dark Embrace": 75,
    "Evolve": 68,
    "Second Wind": 70,
    "Seeing Red": 67,
    "Bloodletting": 38,
    "Pummel": 68,
    "Sword Boomerang": 65,
    "Thunderclap": 64,
    "Cleave": 64,
    "Headbutt": 66,
    "Burning Pact": 65,
    "Dual Wield": 60,
    "Juggernaut": 64,
    "Double Tap": 66,
    "Exhume": 65,
    "Intimidate": 63,
    "Rage": 62,
    "Entrench": 58,
    # B-Tier Early Act 1 / Filler
    "Anger": 61,
    "Iron Wave": 59,
    "Flex": 55,
    "Combust": 58,
    "Fire Breathing": 56,
    "Perfected Strike": 54,
    "Sever Soul": 55,
    "Rampage": 54,
    "Dropkick": 52,
    "Warcry": 52,
    "Wild Strike": 50,
    "Reckless Charge": 48,
    # Colorless Good Cards
    "Apotheosis": 99,
    "Master of Strategy": 90,
    "Panacea": 70,
    "Blind": 68,
    "Trip": 66,
    "Dark Shackles": 78,
    "Finesse": 70,
    "Flash of Steel": 72,
    "Good Instincts": 62,
    "Bandage Up": 72,
}

UPGRADE_PRIORITY = [
    "Apotheosis", "Demon Form", "Reaper", "Whirlwind", "Immolate", "Bash", "Uppercut", "Inflame",
    "Limit Break", "Spot Weakness", "Armaments", "Shockwave",
    "Offering", "Carnage", "Hemokinesis", "True Grit", "Pommel Strike",
    "Shrug It Off", "Flame Barrier", "Impervious", "Body Slam", "Heavy Blade",
    "Feel No Pain", "Dark Embrace", "Corruption", "Disarm", "Battle Trance",
    "Clothesline", "Twin Strike", "Bludgeon", "Blood for Blood", "Metallicize",
    "Power Through", "Cleave", "Thunderclap", "Ghostly Armor", "Headbutt",
    "Defend_R", "Strike_R"
]

BOSS_RELIC_SCORES = {
    "Sozu": 98,
    "Cursed Key": 96,
    "Snecko Eye": 95,
    "Fusion Hammer": 94,
    "Slaver's Collar": 92,
    "Philosopher's Stone": 91,
    "Ectoplasm": 89,
    "Velvet Choker": 88,
    "Mark of Pain": 87,
    "Busted Crown": 84,
    "Black Blood": 75,
    "Astrolabe": 73,
    "Empty Cage": 72,
    "Calling Bell": 70,
    "Black Star": 68,
    "SacredBark": 67,
    "Runic Cube": 66,
    "Tiny House": 62,
    "Runic Pyramid": 50,
    "Coffee Dripper": 42,
    "Pandora's Box": 30,
    "Runic Dome": 20,
}

def get_power_amt(entity, power_id):
    for p in entity.get("powers", []):
        if p.get("id") == power_id or p.get("name") == power_id:
            return p.get("amount", 0)
    return 0

def has_relic(player, relic_id):
    for r in player.get("relics", []):
        if r.get("id") == relic_id or r.get("name") == relic_id:
            return True
    return False

def count_card_in_deck(master_deck, card_id):
    return sum(1 for c in master_deck if c.get("id") == card_id)

def evaluate_card_for_deck(card, st):
    cid = card.get("id", "")
    base = CARD_SCORES.get(cid, 40)
    if card.get("upgraded"):
        base += 12
    player = st.get("player", {})
    deck = player.get("masterDeck", [])
    act = st.get("dungeon", {}).get("actNum", 1)
    floor = st.get("dungeon", {}).get("floorNum", 1)

    copies = count_card_in_deck(deck, cid)
    # Avoid duplicates of powers, 3-cost cards, or situational cards
    three_cost_count = sum(1 for c in deck if c.get("cost", 0) >= 3)
    if card.get("cost", 0) >= 3 and three_cost_count >= 1 and cid != "Corruption":
        base -= 22 * three_cost_count
    if cid in ("Demon Form", "Corruption", "Barricade", "Bludgeon", "Body Slam", "Spot Weakness", "Feed", "Reaper", "Fiend Fire", "Second Wind") and copies >= 1:
        base -= 35
    elif card.get("type") == "POWER" and copies >= 2:
        base -= 35
    elif copies >= 2 and cid not in ("Shrug It Off", "Pommel Strike", "Twin Strike", "Offering"):
        base -= 20
    elif copies >= 3:
        base -= 35

    # Synergies
    has_str = any(c.get("id") in ("Inflame", "Spot Weakness", "Demon Form", "Rupture") for c in deck) or has_relic(player, "Vajra") or has_relic(player, "Girya") or has_relic(player, "Du-Vu Doll")
    has_exhaust = any(c.get("id") in ("Corruption", "Feel No Pain", "Dark Embrace", "True Grit", "Fiend Fire", "Second Wind") for c in deck)
    has_block = any(c.get("id") in ("Barricade", "Entrench", "Impervious", "Flame Barrier", "Power Through", "Metallicize") for c in deck)

    if cid in ("Limit Break", "Heavy Blade", "Sword Boomerang", "Twin Strike", "Pummel", "Reaper"):
        if has_str:
            base += 15
        elif cid == "Limit Break":
            base -= 35  # Don't take Limit Break with zero strength sources

    if cid == "Body Slam" and has_block:
        base += 14
    if cid == "Entrench" and not has_block:
        base -= 25
    if cid in ("Feel No Pain", "Dark Embrace", "Sentinel") and has_exhaust:
        base += 12

    # In Act 1, ensure we draft at least 5 strong non-Strike Attack cards so we have enough damage for Elites & Slime Boss/Hexaghost
    attack_count = sum(1 for c in deck if c.get("type") == "ATTACK" and c.get("id") not in ("Strike_R", "Body Slam"))
    if act == 1:
        if card.get("type") == "ATTACK" and attack_count < 5 and base >= 54:
            base += 18
        elif card.get("type") == "SKILL" and attack_count < 3 and base < 82:
            base -= 16

    # Deck size control: as deck grows larger (> 22), raise the bar for common filler cards
    deck_size = len(deck)
    if deck_size >= 22 and base < 72:
        base -= 20
    elif deck_size >= 17 and base < 65:
        base -= 12

    return base

class IroncladBot:
    def __init__(self):
        self.screenshots_taken = set()
        self.last_floor = -1
        self.last_room_class = ""
        self.combat_turn_logged = (-1, -1)
        self.shop_visited_floors = set()
        self.shop_clicks_per_floor = {}
        self.potion_tries = {}
        self.skipped_card_floors = set()

    def maybe_screenshot(self, key, filename):
        if key not in self.screenshots_taken:
            self.screenshots_taken.add(key)
            screenshot(filename)

    def handle_main_menu(self, st):
        mm = st.get("mainMenu", {})
        scr = mm.get("screen")
        if scr == "MAIN_MENU":
            for b in mm.get("buttons", []):
                if b.get("result") == "PLAY":
                    log("Main Menu: Clicking PLAY")
                    click(b["hb"]["cx"], b["hb"]["cy"], 0.8)
                    return
        elif scr == "PANEL_MENU":
            for p in mm.get("panels", []):
                if p.get("result") == "PLAY_NORMAL":
                    log("Panel Menu: Clicking PLAY_NORMAL")
                    click(p["hb"]["cx"], p["hb"]["cy"], 0.8)
                    return
        elif scr == "CHAR_SELECT":
            cs = mm.get("charSelect", {})
            for opt in cs.get("options", []):
                if opt.get("chosenClass") == "IRONCLAD" and not opt.get("selected"):
                    log("Char Select: Selecting IRONCLAD")
                    click(opt["hb"]["cx"], opt["hb"]["cy"], 0.6)
                    return
            if cs.get("isAscensionMode"):
                ahb = cs.get("ascensionHb")
                if ahb:
                    log("Char Select: Disabling Ascension Mode")
                    click(ahb["cx"], ahb["cy"], 0.5)
                    return
            cb = cs.get("confirmButton", {})
            if cb and not cb.get("isHidden"):
                log("Char Select: Clicking Embark")
                click(cb["hb"]["cx"], cb["hb"]["cy"], 1.5)
                return

    def handle_event(self, st):
        ev = st.get("event", {})
        ev_name = ev.get("eventName", "UnknownEvent")
        opts = [o for o in ev.get("roomEventOptions", []) if not o.get("isDisabled") and not o.get("pressed")]
        if not opts:
            opts = [o for o in ev.get("imageEventOptions", []) if not o.get("isDisabled") and not o.get("pressed")]
        if not opts:
            if ev_name == "GremlinMatchGame":
                coords = [
                    (640, 320), (850, 320), (1060, 320), (1270, 320),
                    (640, 540), (850, 540), (1060, 540), (1270, 540),
                    (640, 760), (850, 760), (1060, 760), (1270, 760),
                ]
                idx = getattr(self, "match_idx", 0)
                self.match_idx = (idx + 1) % len(coords)
                cx, cy = coords[idx]
                log(f"GremlinMatchGame: Clicking card slot [{idx}] at ({cx}, {cy})")
                click(cx, cy, 0.65)
                return True
            elif ev_name == "GremlinWheelGame":
                log("GremlinWheelGame: Clicking wheel spin")
                click(960, 540, 0.8)
                return True
            return False

        floor = st.get("dungeon", {}).get("floorNum", 0)
        act = st.get("dungeon", {}).get("actNum", 1)
        player = st.get("player", {})
        hp = player.get("currentHealth", 80)
        max_hp = player.get("maxHealth", 80)
        gold = player.get("gold", 0)

        if len(opts) == 1:
            chosen = opts[0]
            log(f"Floor {floor} Event ({ev_name}): Clicking single option -> {chosen.get('msg')}")
            click(chosen["hb"]["cx"], chosen["hb"]["cy"], 0.5)
            return True

        # Neow Event on Floor 0
        if floor == 0 or ev_name == "NeowEvent":
            self.maybe_screenshot("neow_options", "03_neow_blessing.png")
            best_opt = opts[0]
            best_score = -999
            for o in opts:
                msg = re.sub(r'#[grybp](?=[a-z0-9])', '', (o.get("msg") or "").lower())
                idx = o.get("index", 0)
                score = 10
                # Strongly avoid Boss Relic Swap (lose Burning Blood)
                if "lose your starting relic" in msg or "boss relic" in msg:
                    score = -100
                elif "curse" in msg:
                    score = -50
                elif "enemies in your next three" in msg or "1 hp" in msg:
                    score = 95
                elif "common relic" in msg or "rare relic" in msg:
                    score = 90
                elif "upgrade a card" in msg:
                    score = 85
                elif "100 gold" in msg:
                    score = 82
                elif "remove a card" in msg:
                    score = 80
                elif "max hp" in msg and "lose" not in msg:
                    score = 78
                elif "choose a card" in msg or "obtain a random rare" in msg:
                    score = 76
                elif idx in (0, 1):
                    score = 70
                if score > best_score:
                    best_score = score
                    best_opt = o
            log(f"Neow Blessing: Choosing [{best_opt.get('index')}] {best_opt.get('msg')}")
            click(best_opt["hb"]["cx"], best_opt["hb"]["cy"], 0.6)
            return True

        # General Event Heuristics
        best_opt = opts[-1]  # Default to Leave/safe option if unsure
        best_score = -999
        for o in opts:
            msg = re.sub(r'#[grybp](?=[a-z0-9])', '', (o.get("msg") or "").lower())
            score = 0
            if "leave" in msg or "ignore" in msg or "continue" in msg or "walk away" in msg or "decline" in msg or "cowardice" in msg or "escape" in msg:
                score = 25
            # Colosseum second fight (Taskmaster + Gremlin Nob) is very dangerous unless HP is high
            if "colosseum" in ev_name.lower() and "victory" in msg:
                score = 60 if hp >= max_hp * 0.78 else -50
            elif "dead adventurer" in ev_name.lower() and "search" in msg:
                score = 45 if hp >= 55 else -40
            elif "knowing skull" in ev_name.lower():
                if "leave" in msg or "how do i leave" in msg:
                    score = 60 if hp < 45 else 15
                elif "gold" in msg and hp >= 45:
                    score = 50
                else:
                    score = -30
            if "heal" in msg and "curse" not in msg and "decay" not in msg and "doubt" not in msg:
                if hp < max_hp * 0.7:
                    score += 65
                else:
                    score += 25
            if "upgrade" in msg and "curse" not in msg:
                score += 60
            if "remove a card" in msg or "purify" in msg:
                if "lose" not in msg or hp > 45:
                    score += 55
            if "relic" in msg and "curse" not in msg and "pain" not in msg and "regret" not in msg and "colosseum" not in ev_name.lower():
                if ("lose" in msg or "damage" in msg or "hp" in msg) and hp < 45:
                    score -= 40
                else:
                    score += 50
            if "max hp" in msg and "lose" not in msg:
                score += 45
            if "gold" in msg and "lose" not in msg and "curse" not in msg and "regret" not in msg and "doubt" not in msg and "shame" not in msg and "normality" not in msg:
                score += 35
            if "curse" in msg or "normality" in msg or "pain" in msg or "regret" in msg or "doubt" in msg or "writhe" in msg or "decay" in msg or "injury" in msg or "shame" in msg or "parasite" in msg:
                score -= 80
            if ("lose all gold" in msg or "lose all of your gold" in msg) and gold > 35:
                score = -100
            if "maskedbandits" in ev_name.lower() and "fight" in msg:
                score = 80 if hp >= 35 else -20
            if ("take " in msg or "lose " in msg) and "hp" in msg:
                if hp < 45:
                    score -= 60
            # Avoid Vampires (Bite) event unless we have Molten Egg / Blood Vial (losing 30% Max HP & adding 5 unupgraded Bites hurts late game)
            if "vampire" in ev_name.lower() and ("accept" in msg or "bite" in msg):
                score = -60
            # Mind Bloom in Act 3: always pick [I am War] (easy Act 1 Boss for Rare Relic), never [I am Awake] (no longer heal)
            if "i am war" in msg or "fight a boss from act 1" in msg:
                score = 120
            if "no longer heal" in msg or "i am awake" in msg:
                score = -200
            if "open sphere" in msg:
                score = -100
            if "embrace madness" in msg or "madness" in msg:
                score = -80
            if "retrace your steps" in msg:
                score = 45
            # Apparitions (Council of Ghosts): very strong even with max HP loss
            if "apparition" in msg:
                score += 75
            # Library: Read (pick 1 of 20 cards) or Sleep (heal)
            if "choose 1 of 20" in msg:
                score += 60
            # Golden Idol: Take Idol -> then take damage or lose max HP
            if "take" in msg and "golden idol" in ev_name.lower():
                score += 55
            if "outmaneuver" in msg or "smash" in msg:
                score += 50
            if score > best_score:
                best_score = score
                best_opt = o

        log(f"Floor {floor} Event ({ev_name}): Choosing [{best_opt.get('index')}] {best_opt.get('msg')}")
        click(best_opt["hb"]["cx"], best_opt["hb"]["cy"], 0.6)
        return True

    def handle_grid_select(self, st):
        gs = st.get("gridSelect", {})
        if gs.get("confirmScreenUp") or gs.get("isJustForConfirming"):
            cb = gs.get("confirmButton", {})
            if cb and not cb.get("isHidden") and not cb.get("isDisabled"):
                log("Grid Select: Clicking Confirm (confirmScreenUp)")
                click(cb["hb"]["cx"], cb["hb"]["cy"], 0.5)
                return
        cb = gs.get("confirmButton", {})
        num_cards = gs.get("numCards", 1)
        sel_count = gs.get("selectedCount", 0)
        if cb and not cb.get("isHidden") and not cb.get("isDisabled") and (sel_count >= num_cards or gs.get("anyNumber")):
            log("Grid Select: Clicking Confirm button")
            click(cb["hb"]["cx"], cb["hb"]["cy"], 0.5)
            return

        cards = gs.get("cards", [])
        if not cards:
            # Check overlay cancel if stuck
            ca = st.get("overlay", {}).get("cancel", {})
            if ca and not ca.get("isHidden"):
                click(ca["hb"]["cx"], ca["hb"]["cy"], 0.5)
            return

        if sel_count == 0 or not hasattr(self, "grid_selected_indices"):
            self.grid_selected_indices = set()

        avail_cards = [c for c in cards if c.get("index") not in self.grid_selected_indices]
        if not avail_cards:
            avail_cards = cards

        # Decide which card to pick based on mode
        chosen = None
        if gs.get("forUpgrade"):
            best_rank = 999
            for c in avail_cards:
                cid = c.get("id", "")
                rank = UPGRADE_PRIORITY.index(cid) if cid in UPGRADE_PRIORITY else 100
                if rank < best_rank:
                    best_rank = rank
                    chosen = c
        elif gs.get("forPurge") or gs.get("forTransform") or num_cards >= 2:
            # Priority to remove/transform (including Astrolabe numCards=3 & Empty Cage numCards=2):
            deck = st.get("player", {}).get("masterDeck", [])
            act = st.get("dungeon", {}).get("actNum", 1)
            attack_count = sum(1 for c in deck if c.get("type") == "ATTACK" and c.get("id") != "Strike_R")
            prefer_defend_purge = (act == 1 and attack_count < 3 and gs.get("forPurge"))
            best_purge_score = -999
            for c in avail_cards:
                cid = c.get("id", "")
                ctype = c.get("type", "")
                if ctype == "CURSE" or cid in ("AscendersBane", "Parasite", "Regret", "Pain", "Doubt", "Decay", "Shame", "Writhe", "Injury", "Clumsy", "Normality"):
                    ps = 200
                elif cid == "Defend_R" and not c.get("upgraded") and prefer_defend_purge:
                    ps = 160
                elif cid == "Strike_R" and not c.get("upgraded"):
                    ps = 150
                elif cid == "Defend_R" and not c.get("upgraded"):
                    ps = 120
                elif cid == "Strike_R":
                    ps = 110
                else:
                    ps = 100 - CARD_SCORES.get(cid, 45)
                if ps > best_purge_score:
                    best_purge_score = ps
                    chosen = c
        else:
            # General selection (e.g. Headbutt from discard, Exhume from exhaust, Library 1 of 20, etc.)
            in_combat = st.get("room", {}).get("phase") == "COMBAT"
            low_enemy = any(0 < m.get("currentHealth", 0) <= 30 for m in st.get("monsters", []) if not m.get("isDead"))
            best_val = -999
            for c in avail_cards:
                cid = c.get("id", "")
                ctype = c.get("type", "")
                val = CARD_SCORES.get(cid, 50) + (10 if c.get("upgraded") else 0)
                if in_combat:
                    if cid in ("Spot Weakness", "Feed", "Demon Form", "Corruption", "Barricade"):
                        val -= 45  # Don't put slow/situational cards on top of draw pile with Headbutt!
                    if low_enemy and ctype == "ATTACK" and cid != "Feed":
                        val += 40  # Put a finishing Attack on top of draw pile when enemy is low!
                if val > best_val:
                    best_val = val
                    chosen = c

        if chosen is None:
            chosen = avail_cards[0]

        hb = chosen.get("hb", {})
        cy = hb.get("cy", 500)
        # Scroll if card is off-screen
        if cy < 140:
            log(f"Grid Select: Card {chosen.get('name')} at cy={cy:.1f} (<140), scrolling down")
            scroll_api("down", 6, 0.3)
            return
        elif cy > 930:
            log(f"Grid Select: Card {chosen.get('name')} at cy={cy:.1f} (>930), scrolling up")
            scroll_api("up", 6, 0.3)
            return

        self.grid_selected_indices.add(chosen.get("index"))
        log(f"Grid Select: Clicking card [{chosen.get('index')}] {chosen.get('name')} at ({hb.get('cx'):.1f}, {cy:.1f})")
        click(hb["cx"], cy, 0.5)

    def handle_hand_select(self, st):
        hs = st.get("handSelect", {})
        num_to_sel = hs.get("numCardsToSelect", 1)
        num_sel = max(hs.get("numSelected", 0), len(hs.get("selectedCards", [])))
        cb = hs.get("confirmButton", {})
        hand_cards = hs.get("handCards", [])
        reason = (hs.get("selectionReason") or "").lower()
        for_upgrade = hs.get("forUpgrade", False)

        if len(hand_cards) == 0 or num_sel >= num_to_sel:
            if cb and not cb.get("isHidden") and not cb.get("isDisabled"):
                log("Hand Select: Confirming selection")
                click(cb["hb"]["cx"], cb["hb"]["cy"], 0.4)
                return

        if hand_cards:
            best_idx = 0
            if for_upgrade or "upgrade" in reason:
                best_rank = 999
                for i, c in enumerate(hand_cards):
                    cid = c.get("id", "")
                    rank = UPGRADE_PRIORITY.index(cid) if cid in UPGRADE_PRIORITY else 100
                    if rank < best_rank:
                        best_rank = rank
                        best_idx = i
            elif "copy" in reason or "dual wield" in reason:
                best_val = -999
                for i, c in enumerate(hand_cards):
                    val = CARD_SCORES.get(c.get("id", ""), 50)
                    if val > best_val:
                        best_val = val
                        best_idx = i
            else:
                # Exhaust / Discard / Put on top of deck: pick Status/Curse/Strike/Defend first
                best_pri = -999
                for i, c in enumerate(hand_cards):
                    cid = c.get("id", "")
                    ctype = c.get("type", "")
                    if ctype in ("STATUS", "CURSE"):
                        pri = 200
                    elif cid == "Sentinel":
                        pri = 190
                    elif cid == "Strike_R":
                        pri = 150
                    elif cid == "Defend_R":
                        pri = 140
                    else:
                        pri = 100 - CARD_SCORES.get(cid, 50)
                    if pri > best_pri:
                        best_pri = pri
                        best_idx = i

                # For optional discard/replace effects (Gambling Chip, Gambler's Brew), stop once only good cards remain!
                if (hs.get("anyNumber") or hs.get("canPickZero") or "replace" in reason or "gambl" in reason) and best_pri < 140:
                    if cb and not cb.get("isHidden") and not cb.get("isDisabled"):
                        log(f"Hand Select ({reason}): Keeping remaining good cards -> Confirming selection")
                        click(cb["hb"]["cx"], cb["hb"]["cy"], 0.4)
                        return

            log(f"Hand Select ({reason}): Selecting hand card [{best_idx}] {hand_cards[best_idx].get('name')}")
            hand_select_api(best_idx, 0.35)

    def handle_card_reward(self, st):
        cr = st.get("cardReward", {})
        cards = cr.get("cards", [])
        room = st.get("room", {})
        floor = st.get("dungeon", {}).get("floorNum", 1)
        in_combat = room.get("phase") == "COMBAT" and not room.get("isBattleOver")

        best_card = None
        best_score = -999
        for c in cards:
            sc = evaluate_card_for_deck(c, st)
            if sc > best_score:
                best_score = sc
                best_card = c

        # In combat (e.g. Discovery / Infernal Blade), you MUST pick a card
        threshold = -999 if in_combat else 56
        if best_card and best_score >= threshold:
            log(f"Card Reward: Picking {best_card.get('name')} (score={best_score})")
            click(best_card["hb"]["cx"], best_card["hb"]["cy"], 0.6)
            return

        if not in_combat:
            self.skipped_card_floors.add(floor)

        # Singing Bowl (+2 Max HP) if available when skipping
        bowl = cr.get("bowlButton", {})
        if bowl and not bowl.get("isHidden"):
            log("Card Reward: Clicking Singing Bowl (+2 Max HP)")
            click(bowl["hb"]["cx"], bowl["hb"]["cy"], 0.5)
            return

        skip = cr.get("skipButton", {})
        if skip and not skip.get("isHidden"):
            log(f"Card Reward: Skipping (best was {best_card.get('name') if best_card else 'None'} score={best_score})")
            click(skip["hb"]["cx"], skip["hb"]["cy"], 0.5)
            return

        ca = st.get("overlay", {}).get("cancel", {})
        if ca and not ca.get("isHidden"):
            click(ca["hb"]["cx"], ca["hb"]["cy"], 0.5)

    def handle_combat_reward(self, st):
        rews = st.get("combatRewards", [])
        floor = st.get("dungeon", {}).get("floorNum", 1)
        player = st.get("player", {})
        pots = player.get("potions", [])
        has_empty_pot = any(p.get("isEmpty") for p in pots)
        has_cursed_key = has_relic(player, "Cursed Key")

        for r in rews:
            if r.get("isDone") or r.get("ignoreReward"):
                continue
            rtype = r.get("type")
            if rtype == "CARD" and floor in self.skipped_card_floors:
                continue
            if rtype in ("GOLD", "STOLEN_GOLD", "RELIC", "CARD"):
                log(f"Combat Reward: Claiming {rtype} ({r.get('text')})")
                click(r["hb"]["cx"], r["hb"]["cy"], 0.5)
                return
            elif rtype == "POTION":
                if has_relic(player, "Sozu"):
                    continue
                if has_empty_pot:
                    log(f"Combat Reward: Claiming POTION ({r.get('text')})")
                    click(r["hb"]["cx"], r["hb"]["cy"], 0.5)
                    return
            elif rtype in ("SAPPHIRE_KEY", "EMERALD_KEY"):
                # Don't take Sapphire Key over a Relic
                continue

        pr = st.get("overlay", {}).get("proceed", {})
        if pr and not pr.get("isHidden"):
            log("Combat Reward: Clicking Proceed")
            click(pr["hb"]["cx"], pr["hb"]["cy"], 0.6)

    def handle_boss_relic(self, st):
        act = st.get("dungeon", {}).get("actNum", 1)
        self.maybe_screenshot(f"boss_relic_act{act}", f"act{act}_boss_relics.png")
        brelics = st.get("bossRelics", [])
        if not brelics:
            pr = st.get("overlay", {}).get("proceed", {})
            if pr and not pr.get("isHidden"):
                click(pr["hb"]["cx"], pr["hb"]["cy"], 0.6)
            return

        best_r = brelics[0]
        best_sc = -999
        for r in brelics:
            rid = r.get("id", "")
            sc = BOSS_RELIC_SCORES.get(rid, 60)
            if sc > best_sc:
                best_sc = sc
                best_r = r

        log(f"Boss Relic: Picking {best_r.get('name')} ({best_r.get('id')}, score={best_sc})")
        click(best_r["hb"]["cx"], best_r["hb"]["cy"], 0.8)

    def handle_campfire(self, st):
        cf = st.get("campfire", {})
        if cf.get("somethingSelected"):
            pr = st.get("overlay", {}).get("proceed", {})
            if pr and not pr.get("isHidden"):
                click(pr["hb"]["cx"], pr["hb"]["cy"], 0.5)
            return

        opts = [o for o in cf.get("options", []) if o.get("usable")]
        if not opts:
            pr = st.get("overlay", {}).get("proceed", {})
            if pr and not pr.get("isHidden"):
                click(pr["hb"]["cx"], pr["hb"]["cy"], 0.5)
            return

        player = st.get("player", {})
        hp = player.get("currentHealth", 80)
        max_hp = player.get("maxHealth", 80)
        floor = st.get("dungeon", {}).get("floorNum", 1)
        act = st.get("dungeon", {}).get("actNum", 1)

        self.maybe_screenshot(f"campfire_act{act}", f"act{act}_campfire_floor{floor}.png")

        # Check if before Boss (floor 15, 32, 49)
        before_boss = floor in (15, 32, 49)
        rest_threshold = 0.80 if before_boss else 0.65

        rest_opt = next((o for o in opts if o.get("type") == "RestOption"), None)
        smith_opt = next((o for o in opts if o.get("type") == "SmithOption"), None)
        lift_opt = next((o for o in opts if o.get("type") == "LiftOption"), None)
        dig_opt = next((o for o in opts if o.get("type") == "DigOption"), None)

        if rest_opt and (hp / max(1, max_hp)) < rest_threshold:
            log(f"Campfire (Floor {floor}, HP {hp}/{max_hp}): Choosing REST")
            click(rest_opt["hb"]["cx"], rest_opt["hb"]["cy"], 0.8)
            return
        if lift_opt and hp > max_hp * 0.65:
            log(f"Campfire (Floor {floor}): Choosing LIFT (Girya +1 Str)")
            click(lift_opt["hb"]["cx"], lift_opt["hb"]["cy"], 0.8)
            return
        if smith_opt:
            log(f"Campfire (Floor {floor}, HP {hp}/{max_hp}): Choosing SMITH")
            click(smith_opt["hb"]["cx"], smith_opt["hb"]["cy"], 0.8)
            return
        if dig_opt:
            log(f"Campfire (Floor {floor}): Choosing DIG")
            click(dig_opt["hb"]["cx"], dig_opt["hb"]["cy"], 0.8)
            return
        if rest_opt:
            log(f"Campfire (Floor {floor}): Choosing REST (fallback)")
            click(rest_opt["hb"]["cx"], rest_opt["hb"]["cy"], 0.8)
            return

        chosen = opts[0]
        log(f"Campfire (Floor {floor}): Choosing {chosen.get('type')}")
        click(chosen["hb"]["cx"], chosen["hb"]["cy"], 0.8)

    def handle_shop(self, st):
        floor = st.get("dungeon", {}).get("floorNum", 1)
        act = st.get("dungeon", {}).get("actNum", 1)
        sh = st.get("shop", {})
        scr = st.get("dungeon", {}).get("screen")

        if scr != "SHOP":
            if floor not in self.shop_visited_floors:
                mhb = sh.get("merchantHb")
                if mhb:
                    log(f"Shop Room (Floor {floor}): Opening Merchant")
                    click(mhb["cx"], mhb["cy"], 0.7)
                    return
            pr = st.get("overlay", {}).get("proceed", {})
            if pr and not pr.get("isHidden"):
                log(f"Shop Room (Floor {floor}): Clicking Proceed")
                click(pr["hb"]["cx"], pr["hb"]["cy"], 0.6)
                return

        self.shop_visited_floors.add(floor)
        self.maybe_screenshot(f"shop_act{act}", f"act{act}_shop_floor{floor}.png")

        clicks = self.shop_clicks_per_floor.get(floor, 0)
        if clicks < 4:
            self.shop_clicks_per_floor[floor] = clicks + 1
            player = st.get("player", {})
            gold = player.get("gold", 0)
            deck = player.get("masterDeck", [])

            # 1. Card Removal (Purge) if we have a Curse or unupgraded Strike_R and enough gold
            has_curse_or_strike = any(c.get("type") == "CURSE" or c.get("id") == "Strike_R" for c in deck)
            if sh.get("purgeAvailable") and has_curse_or_strike and gold >= sh.get("purgeCost", 75) and clicks == 0:
                px, py = sh.get("purgeX", 0), sh.get("purgeY", 0)
                if px > 0 and py > 0:
                    log(f"Shop: Purchasing Card Removal for {sh.get('purgeCost')}g")
                    click(px, py, 0.7)
                    return

            # 2. Check great affordable Relics
            for rel in sh.get("relics", []):
                if not rel.get("isPurchased") and rel.get("price", 999) <= gold:
                    rid = rel.get("id", "")
                    if rid not in ("Dead Branch", "Strange Spoon", "Bottled Flame", "PrismaticShard", "Prismatic Shard", "Runic Dome"):
                        log(f"Shop: Buying Relic {rel.get('name')} for {rel.get('price')}g")
                        click(rel["hb"]["cx"], rel["hb"]["cy"], 0.6)
                        return

            # 3. Check top-tier Cards (score >= 78)
            all_shop_cards = sh.get("coloredCards", []) + sh.get("colorlessCards", [])
            best_c = None
            best_sc = 77
            for c in all_shop_cards:
                price = c.get("price", 999)
                if price <= gold:
                    sc = evaluate_card_for_deck(c, st)
                    if sc > best_sc:
                        best_sc = sc
                        best_c = c
            if best_c:
                log(f"Shop: Buying Card {best_c.get('name')} for {best_c.get('price')}g (score={best_sc})")
                click(best_c["hb"]["cx"], best_c["hb"]["cy"], 0.6)
                return

        # 4. Close shop
        ca = st.get("overlay", {}).get("cancel", {})
        if ca and not ca.get("isHidden"):
            log("Shop: Closing Shop screen")
            click(ca["hb"]["cx"], ca["hb"]["cy"], 0.6)

    def handle_map(self, st):
        mp = st.get("map", {})
        scr = st.get("dungeon", {}).get("screen")
        if scr != "MAP":
            tp = st.get("overlay", {}).get("topPanel", {})
            mhb = tp.get("mapHb")
            if mhb and not tp.get("mapDisabled"):
                click(mhb["cx"], mhb["cy"], 0.6)
            return

        # Check if at Boss (ONLY when currY == 14, i.e. the campfire before the Boss!)
        if mp.get("currY") == 14:
            bhb = mp.get("bossHb", {})
            cy = bhb.get("cy", 500)
            if cy > 900:
                log(f"Map: Boss node at cy={cy:.1f} (>900), scrolling up")
                scroll_api("up", 8, 0.3)
                return
            elif cy < 150:
                log(f"Map: Boss node at cy={cy:.1f} (<150), scrolling down")
                scroll_api("down", 8, 0.3)
                return
            log(f"Map: Clicking Boss node at ({bhb.get('cx'):.1f}, {cy:.1f})")
            click(bhb["cx"], cy, 1.0)
            return

        nodes = mp.get("nodes", [])
        playable = [n for n in nodes if n.get("playable")]
        if not playable:
            return

        # Build adjacency map to score 3 steps ahead
        node_lookup = {(n["x"], n["y"]): n for n in nodes}
        player = st.get("player", {})
        hp_ratio = player.get("currentHealth", 80) / max(1, player.get("maxHealth", 80))
        gold = player.get("gold", 0)
        act = st.get("dungeon", {}).get("actNum", 1)

        def score_node(n, depth=0):
            sym = n.get("symbol", "")
            s = 0.0
            if sym == "R":
                s = 40.0 if hp_ratio < 0.7 else 30.0
            elif sym == "$":
                s = 32.0 if gold >= 150 else 5.0
            elif sym == "T":
                s = 35.0
            elif sym == "?":
                s = 22.0
            elif sym == "M":
                s = 18.0
            elif sym == "E":
                if n.get("hasEmeraldKey"):
                    s = -25.0  # Avoid Burning Elite when not going for Heart
                elif hp_ratio >= 0.72 and act == 1:
                    s = 28.0
                elif hp_ratio >= 0.78 and act == 2:
                    s = 22.0
                elif hp_ratio >= 0.90 and act == 3:
                    s = 12.0  # In Act 3, prefer safe rooms (?, M, R, $, T) to preserve HP for the Floor 50 Boss!
                else:
                    s = -30.0
            if depth < 3:
                edges = n.get("edges", [])
                child_scores = []
                for e in edges:
                    child = node_lookup.get((e.get("dstX"), e.get("dstY")))
                    if child:
                        child_scores.append(score_node(child, depth + 1))
                if child_scores:
                    s += 0.65 * max(child_scores)
            return s

        best_node = max(playable, key=lambda n: score_node(n, 0))
        hb = best_node.get("hb", {})
        cy = hb.get("cy", 500)

        if cy > 880:
            log(f"Map: Target node ({best_node['x']},{best_node['y']} {best_node['symbol']}) at cy={cy:.1f} (>880), scrolling up")
            scroll_api("up", 6, 0.3)
            return
        elif cy < 160:
            log(f"Map: Target node ({best_node['x']},{best_node['y']} {best_node['symbol']}) at cy={cy:.1f} (<160), scrolling down")
            scroll_api("down", 6, 0.3)
            return

        log(f"Map: Selecting node ({best_node['x']}, {best_node['y']}) [{best_node['symbol']}] at ({hb['cx']:.1f}, {cy:.1f})")
        click(hb["cx"], cy, 0.8)

    def try_use_potion(self, st, alive_monsters, incoming_dmg):
        player = st.get("player", {})
        pui = player.get("potionPopUp", {})
        # Note: in PotionPopUp.update(), when targetMode is true, isHidden is ALSO true!
        if pui.get("targetMode"):
            if alive_monsters:
                target = alive_monsters[0]
                log(f"Potion Target Mode: Clicking monster {target.get('name')}")
                click(target["hb"]["cx"], target["hb"]["cy"], 0.5)
                return True
        if not pui.get("isHidden", True):
            top_hb = pui.get("topHb")
            if top_hb:
                log("Potion PopUp Open: Clicking top button (Use/Drink)")
                click(top_hb["cx"], top_hb["cy"], 0.5)
                return True

        floor = st.get("dungeon", {}).get("floorNum", 1)
        room_cls = st.get("room", {}).get("className", "")
        is_elite_or_boss = "Elite" in room_cls or "Boss" in room_cls
        turn = st.get("actionManager", {}).get("turn", 1)
        hp = player.get("currentHealth", 80)
        max_hp = player.get("maxHealth", 80)
        block = player.get("currentBlock", 0)
        unblocked = max(0, incoming_dmg - block)

        for pot in player.get("potions", []):
            if pot.get("isEmpty") or not pot.get("canUse"):
                continue
            slot = pot.get("slot", 0)
            key = (floor, turn, slot)
            if self.potion_tries.get(key, 0) >= 2:
                continue
            pid = pot.get("id", "")
            pname = pot.get("name", "")
            should_use = False
            if pid == "Fruit Juice":
                should_use = True
            elif pid == "EntropicBrew" and (is_elite_or_boss or hp < max_hp * 0.5):
                should_use = True
            elif pid == "BloodPotion" and hp < max_hp * 0.65:
                should_use = True
            elif pid in ("Regen Potion", "CultistPotion", "Strength Potion", "Dexterity Potion", "EssenceOfSteel", "HeartOfIron", "LiquidBronze", "Ancient Potion", "DuplicationPotion", "BlessingOfTheForge") and ((is_elite_or_boss and turn <= 2) or (hp <= 38 and unblocked >= 10) or unblocked >= 18):
                should_use = True
            elif pid in ("FearPotion", "Fire Potion", "Explosive Potion", "SteroidPotion", "SpeedPotion", "AttackPotion", "PowerPotion", "ColorlessPotion", "SkillPotion", "LiquidMemories") and (is_elite_or_boss or unblocked >= 14 or (hp <= 38 and unblocked >= 8)):
                should_use = True
            elif pid in ("Block Potion", "Swift Potion", "Energy Potion", "SneckoOil", "DistilledChaos") and (unblocked >= 10 or (is_elite_or_boss and unblocked >= 6)):
                should_use = True

            if should_use:
                self.potion_tries[key] = self.potion_tries.get(key, 0) + 1
                log(f"Combat: Opening Potion [{slot}] {pname}")
                click(pot["hb"]["cx"], pot["hb"]["cy"], 0.4)
                return True
        return False

    def choose_best_target(self, card, alive_monsters):
        if not alive_monsters:
            return -1
        if len(alive_monsters) == 1:
            return alive_monsters[0]["index"]

        cid = card.get("id", "")
        dmg = card.get("damage", 0)

        best_m = alive_monsters[0]
        best_score = -9999.0

        for m in alive_monsters:
            mid = m.get("id", "")
            mname = m.get("name", "")
            mhp = m.get("currentHealth", 1)
            mblk = m.get("currentBlock", 0)
            eff_hp = mhp + mblk
            intent = m.get("intent", "")
            is_attacking = "ATTACK" in intent and m.get("intentDmg", 0) > 0
            atk_dmg = (m.get("intentDmg", 0) * (m.get("intentMultiAmt", 1) if m.get("isMultiDmg") and m.get("intentMultiAmt", 1) > 0 else 1)) if is_attacking else 0

            sc = 0.0
            vuln = get_power_amt(m, "Vulnerable")
            eff_dmg = int(dmg * 1.5) if vuln > 0 else dmg
            # Lethal kill priority (strongly prefer killing attacking enemies first!)
            if eff_dmg >= eff_hp and card.get("type") == "ATTACK":
                if is_attacking:
                    sc += 650.0 + atk_dmg * 15.0
                else:
                    sc += 260.0
            # Focus fire enemies that already have Vulnerable!
            if vuln > 0 and card.get("type") == "ATTACK":
                sc += 110.0
            # Finish off Bosses when their HP is getting low (kills all minions immediately!)
            if any(b in mid or b in mname for b in ("TheCollector", "Collector", "BronzeAutomaton", "Automaton", "GremlinLeader")) and eff_hp <= 95:
                sc += 280.0
            # High priority targets
            if "Donu" in mname or mid == "Donu":
                sc += 180.0
            if "BronzeOrb" in mid or mname == "Orb":
                sc += 190.0
            if "Dagger" in mname or "Minion" in mname or "Gremlin" in mname or "TorchHead" in mid:
                if eff_hp <= 22:
                    sc += 140.0
                elif cid not in ("Bash", "Uppercut"):
                    sc += 60.0
            if "SlaverRed" in mid or "Taskmaster" in mid or "Mugger" in mid or "Looter" in mid or "Healer" in mid or "Mystic" in mname:
                sc += 100.0
            if "Sentry" in mid and m["index"] in (0, 2):
                sc += 80.0
            if is_attacking:
                sc += 50.0 + atk_dmg * 3.0

            # If card applies Vulnerable (Bash, Uppercut), prefer target without Vulnerable ONLY if no target is already low/vulnerable
            if cid in ("Bash", "Uppercut", "Trip"):
                if vuln == 0 and mhp >= 22:
                    sc += 65.0
            elif cid in ("Clothesline", "Disarm", "Blind", "Dark Shackles"):
                if is_attacking:
                    sc += 150.0 + atk_dmg * 5.0
            # Focus fire lower HP enemies (so Slimes/Sentries/Minions die one by one instead of splitting/attacking together!)
            sc -= eff_hp * 1.1
            # Avoid hitting Spiker (Thorns) with multi-hit attacks when other targets exist!
            thorns = get_power_amt(m, "Thorns")
            if thorns > 0 and card.get("type") == "ATTACK":
                sc -= thorns * (85.0 if cid in ("Pummel", "Twin Strike") else 25.0)

            if sc > best_score:
                best_score = sc
                best_m = m

        return best_m["index"]

    def handle_combat(self, st):
        am = st.get("actionManager", {})
        if am.get("phase") != "WAITING_ON_USER" or am.get("turnHasEnded") or am.get("actionsCount", 0) > 0 or am.get("cardQueueCount", 0) > 0 or am.get("usingCard"):
            time.sleep(0.15)
            return

        player = st.get("player", {})
        if player.get("isEndingTurn"):
            time.sleep(0.2)
            return

        floor = st.get("dungeon", {}).get("floorNum", 1)
        act = st.get("dungeon", {}).get("actNum", 1)
        turn = am.get("turn", 1)
        room_cls = st.get("room", {}).get("className", "")

        monsters = st.get("monsters", [])
        alive_monsters = [m for m in monsters if not m.get("isDead") and not m.get("isDying") and not m.get("isEscaping") and not m.get("halfDead") and m.get("currentHealth", 0) > 0]
        if not alive_monsters:
            time.sleep(0.2)
            return

        # CRITICAL: Wait until End Turn button is enabled AND all monsters have rolled their Turn 1 intents (not DEBUG)!
        et = st.get("overlay", {}).get("endTurn", {})
        if not et.get("enabled") or et.get("isHidden") or any(m.get("intent") == "DEBUG" for m in alive_monsters):
            time.sleep(0.2)
            return

        # Take screenshots on Turn 1 of Elites and Bosses (and Floor 1)
        if turn == 1:
            if floor == 1:
                self.maybe_screenshot("floor1_combat", "04_act1_first_combat.png")
            elif "Elite" in room_cls:
                self.maybe_screenshot(f"elite_act{act}", f"act{act}_elite_floor{floor}.png")
            elif "Boss" in room_cls:
                self.maybe_screenshot(f"boss_act{act}", f"act{act}_boss_floor{floor}.png")

        # Calculate incoming damage
        incoming_dmg = 0
        any_attacking = False
        for m in alive_monsters:
            intent = m.get("intent", "")
            if "ATTACK" in intent and m.get("intentDmg", 0) > 0:
                any_attacking = True
                mult = m.get("intentMultiAmt", 1) if m.get("isMultiDmg") and m.get("intentMultiAmt", 1) > 0 else 1
                incoming_dmg += m.get("intentDmg", 0) * mult

        # Account for Metallicize / Plated Armor / Orichalcum
        passive_block = get_power_amt(player, "Metallicize") + get_power_amt(player, "Plated Armor")
        curr_block = player.get("currentBlock", 0)
        effective_block = curr_block + passive_block
        if curr_block == 0 and has_relic(player, "Orichalcum"):
            effective_block += 6
        unblocked_dmg = max(0, incoming_dmg - effective_block)

        if self.combat_turn_logged != (floor, turn):
            self.combat_turn_logged = (floor, turn)
            m_summary = ", ".join(f"{m['name']}({m['currentHealth']}+{m['currentBlock']}HP, {m['intent']} {m['intentDmg']}x{m['intentMultiAmt'] if m['isMultiDmg'] else 1})" for m in alive_monsters)
            log(f"Floor {floor} ({room_cls}) Turn {turn}: HP={player.get('currentHealth')}/{player.get('maxHealth')} Blk={curr_block} E={player.get('energy')} Incoming={incoming_dmg} | Enemies: {m_summary}")

        # 1. Check Potions
        if self.try_use_potion(st, alive_monsters, incoming_dmg):
            return

        hand = player.get("hand", [])
        playable = [c for c in hand if c.get("canUse")]
        if not playable:
            log(f"Floor {floor} Turn {turn}: No playable cards left -> End Turn")
            end_turn_api(0.4)
            return

        # Special enemy checks
        has_nob = any("GremlinNob" in m.get("id", "") or "Gremlin Nob" in m.get("name", "") for m in alive_monsters)
        all_sleeping = all(m.get("intent") == "SLEEP" for m in alive_monsters)
        time_eater = next((m for m in alive_monsters if "TimeEater" in m.get("id", "")), None)
        time_warp_cnt = get_power_amt(time_eater, "Time Warp") if time_eater else 0
        awakened_one = next((m for m in alive_monsters if "AwakenedOne" in m.get("id", "")), None)
        curiosity_amt = get_power_amt(awakened_one, "Curiosity") if awakened_one else 0

        # Score each playable card in hand for the current situation
        best_card = None
        best_target = -1
        best_play_score = -1.0

        for c in playable:
            cid = c.get("id", "")
            ctype = c.get("type", "")
            cost = c.get("costForTurn", c.get("cost", 1))
            dmg = c.get("damage", 0)
            blk = c.get("block", 0)
            target_type = c.get("target", "")
            t_idx = self.choose_best_target(c, alive_monsters) if target_type in ("ENEMY", "SELF_AND_ENEMY") else -1

            # Skip X-cost cards at 0 energy
            if c.get("cost") == -1 and player.get("energy", 0) == 0:
                continue

            # Skip Spot Weakness if no monster is attacking, or Limit Break if Strength <= 0!
            if cid == "Spot Weakness" and not any_attacking:
                continue
            if cid == "Limit Break" and get_power_amt(player, "Strength") <= 0:
                continue

            # Against sleeping Lagavulin on Turn 1-2, play Powers/Skills before waking it up with Attacks
            if all_sleeping and turn <= 2 and ctype == "ATTACK":
                if any(other.get("type") == "POWER" for other in playable):
                    continue

            # Time Eater at 11 counter: don't play weak 0-cost cards that end our turn immediately
            if time_warp_cnt == 11 and cost == 0 and cid in ("Anger", "Flex", "Rage", "Intimidate"):
                continue

            # Awakened One Phase 1 (Curiosity): avoid playing minor powers that buff Awakened One +2 Strength!
            if curiosity_amt > 0 and ctype == "POWER" and not (cid in ("Demon Form", "Barricade") or (cid == "Corruption" and has_relic(player, "Snecko Eye"))):
                continue

            # Gremlin Nob: avoid playing Skills unless blocking heavy incoming damage or no Attacks in hand
            has_playable_attack = any(other.get("type") == "ATTACK" for other in playable)
            lethal_incoming = unblocked_dmg >= player.get("currentHealth", 80)
            if has_nob and ctype == "SKILL" and not lethal_incoming:
                if has_playable_attack and cid not in ("Shockwave", "Impervious", "Offering"):
                    continue
                if unblocked_dmg < 8 and cid not in ("Offering", "Shockwave"):
                    continue

            sc = 10.0
            tm = next((m for m in alive_monsters if m["index"] == t_idx), alive_monsters[0]) if t_idx >= 0 else alive_monsters[0]
            target_vuln = get_power_amt(tm, "Vulnerable") > 0
            target_weak = get_power_amt(tm, "Weakened") > 0
            tm_atk_dmg = (tm.get("intentDmg", 0) * (tm.get("intentMultiAmt", 1) if tm.get("isMultiDmg") and tm.get("intentMultiAmt", 1) > 0 else 1)) if "ATTACK" in tm.get("intent", "") else 0
            vuln_mult = (1.75 if has_relic(player, "Paper Frog") else 1.5) if target_vuln else 1.0
            eff_card_dmg = int(dmg * vuln_mult) if ctype == "ATTACK" else dmg
            target_intangible = get_power_amt(tm, "Intangible") > 0 if (t_idx >= 0 and tm) else all(get_power_amt(m, "Intangible") > 0 for m in alive_monsters)
            if target_intangible and ctype == "ATTACK":
                eff_card_dmg = min(eff_card_dmg, 1)

            hits = 1
            if cid in ("Twin Strike", "Uppercut"):
                hits = 2
            elif cid in ("Sword Boomerang", "Pummel"):
                hits = max(1, c.get("magicNumber", 3))
            elif cid == "Whirlwind":
                hits = player.get("energy", 1)
            elif cid == "Fiend Fire":
                hits = max(0, len(hand) - 1)
                if hits == 0:
                    continue

            is_lethal_hit = False
            if ctype == "ATTACK":
                if t_idx >= 0 and tm:
                    is_lethal_hit = (eff_card_dmg * hits) >= (tm.get("currentHealth", 999) + tm.get("currentBlock", 0))
                else:
                    is_lethal_hit = any((eff_card_dmg * hits) >= (m.get("currentHealth", 999) + m.get("currentBlock", 0)) for m in alive_monsters)

            # Intangible enemy discipline (e.g. Nemesis on even turns): all attack damage is capped at 1 per hit!
            if target_intangible and not is_lethal_hit:
                if cid in ("Offering", "Bloodletting", "Hemokinesis"):
                    continue  # Never lose HP when the enemy is Intangible!
                if ctype == "ATTACK" and blk == 0:
                    if cost >= 2:
                        continue  # Never spend 2+ Energy on a 1-damage Attack against an Intangible enemy!
                    if unblocked_dmg > 0 and any(other.get("block", 0) > 0 for other in playable):
                        continue  # Always play all Block cards before poking an Intangible enemy for 1 damage!

            # Time Eater specific card-count & Haste discipline:
            if time_eater and not is_lethal_hit:
                # Never spam Anger or Madness into Time Eater
                if cid in ("Anger", "Madness"):
                    continue
                # On Time Eater's <50% HP Haste (BUFF) turn, it heals back to 228 HP and clears all debuffs!
                # Do NOT waste Attacks, debuffs, or draw/exhaust cards into Haste — only play Powers or Limit Break!
                if time_eater.get("intent") == "BUFF" and time_eater.get("currentHealth", 999) < 228:
                    if ctype != "POWER" and cid != "Limit Break":
                        continue
                # Only stop early at 6..8 on Time Warp when all incoming damage is already blocked so next turn has 4..6 plays.
                # Never stop at 9, 10, or 11 if we have playable cards — push to 12/12 so next turn resets to 0/12!
                if 6 <= time_warp_cnt <= 8 and unblocked_dmg == 0 and ctype != "POWER" and cid != "Limit Break":
                    continue

            # 1. Free / Energy / Draw / Upgrade setup
            if cid == "Apotheosis":
                sc = 400.0 - cost * 15.0
            elif cid == "Rage":
                if has_playable_attack and cost <= 1:
                    sc = 258.0 - cost * 20.0
                else:
                    continue
            elif cid == "Flex":
                if has_playable_attack and cost == 0:
                    sc = 255.0
                else:
                    continue
            elif cid == "Double Tap":
                if has_playable_attack and player.get("energy", 0) >= cost + 1 and cost <= 1:
                    sc = 252.0 - cost * 20.0
                else:
                    continue
            elif cid == "Offering":
                if player.get("currentHealth", 80) > 25 and ("Elite" in room_cls or "Boss" in room_cls or unblocked_dmg >= 18 or any(h.get("id") == "Demon Form" for h in hand)):
                    sc = 320.0
                else:
                    continue
            elif cid in ("Seeing Red", "Adrenaline"):
                if cost <= 1:
                    sc = 300.0 - cost * 30.0
                else:
                    continue
            elif cid == "Bloodletting":
                needed_e = sum(max(0, h.get("costForTurn", 0)) for h in playable if h.get("type") != "STATUS" and h.get("id") != "Bloodletting")
                if player.get("currentHealth", 80) > 50 and needed_e > player.get("energy", 0) and cost == 0 and ("Boss" in room_cls or "Elite" in room_cls or lethal_incoming):
                    sc = 290.0
                else:
                    continue
            elif cid == "Armaments":
                if any(not h.get("upgraded") and h.get("index") != c.get("index") for h in hand) and cost <= 1:
                    sc = 260.0 - cost * 22.0
                else:
                    sc = (90.0 - cost * 18.0) if unblocked_dmg > 0 else 20.0
            elif cid == "Battle Trance":
                if cost >= 2:
                    continue
                elif player.get("energy", 0) >= cost + 1:
                    sc = 250.0 - cost * 35.0
                else:
                    sc = 80.0 - cost * 25.0

            # 2. Powers & Scaling
            elif ctype == "POWER":
                if cid in ("Corruption", "Barricade") and get_power_amt(player, cid) != 0:
                    continue
                if cid == "Corruption" and "Boss" in room_cls and max((m.get("currentHealth", 0) for m in alive_monsters), default=0) > 220 and not has_power_or_relic_barricade(player) and not has_relic(player, "Snecko Eye"):
                    continue  # Don't exhaust all Block cards in Phase 1 of a 400-HP Boss fight unless Snecko Eye or Barricade!
                if lethal_incoming:
                    sc = 5.0  # Don't die playing a Power when lethal is incoming
                else:
                    sc = 235.0 + CARD_SCORES.get(cid, 60) - cost * 18.0
                    if cid == "Corruption" and has_relic(player, "Snecko Eye"):
                        sc += 75.0  # Corruption + Snecko Eye is game-winning!
                    if unblocked_dmg > 0 and cost >= 2 and ((player.get("currentHealth", 80) - unblocked_dmg) <= 30 or (unblocked_dmg >= 15 and turn >= 2)):
                        sc -= unblocked_dmg * 7.5  # Block heavy damage at low/mid HP before tapping out on a 2-3 cost Power!
            elif cid in ("Spot Weakness", "Limit Break"):
                sc = 245.0 - cost * 22.0

            # 3. Debuffs (Vulnerable / Weak / -Str) before attacks
            elif cid == "Shockwave":
                sc = 285.0 - cost * 20.0
            elif cid in ("Disarm", "Dark Shackles") and any_attacking:
                sc = 280.0 - cost * 22.0
            elif cid in ("Blind", "Trip"):
                sc = (255.0 - cost * 22.0) if (any_attacking or cid == "Trip") else (95.0 - cost * 20.0)
            elif cid == "Clothesline" and not target_weak and tm_atk_dmg >= 14 and tm.get("currentHealth", 0) > eff_card_dmg:
                sc = 250.0 + eff_card_dmg * 2.0 - cost * 16.0
            elif cid in ("Bash", "Uppercut", "Thunderclap"):
                if not target_vuln and tm.get("currentHealth", 0) > eff_card_dmg:
                    sc = 238.0 - cost * 22.0 + (20.0 if cid == "Uppercut" and not target_weak and tm_atk_dmg >= 14 else 0.0)
                else:
                    sc = 110.0 + eff_card_dmg * 3.5 - cost * 12.0
            elif cid == "Intimidate":
                sc = (242.0 - cost * 22.0) if any_attacking else (90.0 - cost * 20.0)

            # 4. Block cards when incoming damage > effective_block
            elif blk > 0 and ctype == "SKILL":
                if cid == "Second Wind":
                    non_attacks = sum(1 for h in hand if h.get("type") != "ATTACK" and h.get("index") != c.get("index"))
                    if non_attacks == 0:
                        continue  # Second Wind gives 0 Block when there are 0 non-Attack cards in hand!
                    blk = (blk + get_power_amt(player, "Feel No Pain")) * non_attacks
                if unblocked_dmg > 0:
                    useful_blk = min(blk, unblocked_dmg)
                    urgency_bonus = 65.0 if (unblocked_dmg >= 12 or player.get("currentHealth", 80) <= 50 or "Boss" in room_cls) else 0.0
                    base_blk_sc = 310.0 if lethal_incoming else (135.0 + urgency_bonus)
                    sc = base_blk_sc + useful_blk * 7.5 + (blk - useful_blk) * 0.8 - cost * 12.0
                    if cid == "Second Wind" and any(h.get("block", 0) > 0 and h.get("type") == "SKILL" and h.get("index") != c.get("index") and h.get("costForTurn", 1) <= player.get("energy", 0) - cost for h in playable):
                        sc -= 40.0  # Play other Block skills BEFORE Second Wind exhausts them!
                    # Don't waste 1 energy on Defend just to block 1-3 chip damage when HP > 45 and we have Attacks!
                    if unblocked_dmg <= 3 and not lethal_incoming and player.get("currentHealth", 80) > 45 and has_playable_attack:
                        sc -= 35.0
                    if cid == "Impervious" and unblocked_dmg < 14 and not has_power_or_relic_barricade(player):
                        sc -= 60.0  # Save Impervious for big hits unless needed
                    if cid in ("Shrug It Off", "Flame Barrier", "Power Through", "True Grit", "Ghostly Armor"):
                        sc += 18.0
                    if any(h.get("id") == "Body Slam" for h in playable):
                        sc += 45.0  # Play Block cards first so 0-cost Body Slam deals full block damage!
                else:
                    # No incoming damage left to block
                    if has_power_or_relic_barricade(player) or any(h.get("id") == "Body Slam" for h in hand):
                        sc = 75.0 + blk
                    elif cid == "Shrug It Off" and player.get("energy", 0) >= 2:
                        sc = 65.0  # Cycle draw if nothing better
                    else:
                        continue  # Don't waste energy on Defend when 0 incoming damage!

            # 5. Attacks
            elif ctype == "ATTACK":
                num_targets = len(alive_monsters) if target_type == "ALL_ENEMY" else 1
                total_dmg = eff_card_dmg * hits * num_targets
                if cid == "Body Slam":
                    total_dmg = int(curr_block * vuln_mult)
                    if total_dmg == 0:
                        continue
                eff_cost = player.get("energy", 1) if c.get("cost") == -1 else max(0, cost)
                sc = 100.0 + total_dmg * 3.8 - eff_cost * 10.0
                # Don't tap out on a 3-cost non-lethal Attack (e.g. Bludgeon) when taking heavy unblocked damage and we have Block cards!
                if eff_cost >= 3 and cid != "Whirlwind" and not is_lethal_hit and unblocked_dmg >= 10:
                    if any(other.get("block", 0) > 0 and other.get("type") == "SKILL" for other in playable):
                        sc -= unblocked_dmg * 6.0
                # Splitting Slime Boss (<= 70 HP) cancels its 35-damage Slam!
                if tm and tm.get("id") == "SlimeBoss" and tm.get("currentHealth", 0) > 70 and (tm.get("currentHealth", 0) - eff_card_dmg * hits) <= 70:
                    sc += 250.0
                # Don't let Whirlwind drain all energy before playing Block cards against a single non-lethal enemy!
                if cid == "Whirlwind" and num_targets == 1 and unblocked_dmg > 0:
                    has_blk_card = any(other.get("block", 0) > 0 and other.get("type") == "SKILL" for other in playable)
                    kills_attacker = any(eff_card_dmg * hits >= (m.get("currentHealth", 999) + m.get("currentBlock", 0)) for m in alive_monsters if "ATTACK" in m.get("intent", ""))
                    if has_blk_card and not kills_attacker:
                        sc = min(sc, 125.0)
                # Against Ritual/scaling enemies (like Cultist), prioritize attacking them down!
                if any(get_power_amt(m, "Ritual") > 0 or "Cultist" in m.get("name", "") for m in alive_monsters):
                    sc += 45.0
                if cid == "Reaper":
                    cur_str = get_power_amt(player, "Strength")
                    missing_hp = player.get("maxHealth", 80) - player.get("currentHealth", 80)
                    has_demon_form = get_power_amt(player, "Demon Form") > 0 or any(d.get("id") == "Demon Form" for d in player.get("masterDeck", []))
                    if has_demon_form and cur_str < 4 and not lethal_incoming and turn <= 3:
                        sc -= 65.0  # Wait for Demon Form strength to scale before exhausting Reaper!
                    elif missing_hp >= 8:
                        sc += 95.0 + cur_str * 12.0
                if cid == "Pommel Strike":
                    sc += 15.0

            # Universal Attack post-scoring: Thorns protection & Lethal Kill bonus (never overwritten!)
            if ctype == "ATTACK":
                thorns_on_target = get_power_amt(tm, "Thorns") if t_idx >= 0 else max((get_power_amt(m, "Thorns") for m in alive_monsters), default=0)
                if thorns_on_target > 0:
                    thorns_self_dmg = thorns_on_target * hits
                    if thorns_self_dmg >= curr_block + player.get("currentHealth", 80):
                        continue  # Never suicide into Thorns!
                    unblocked_thorns = max(0, thorns_self_dmg - max(0, curr_block - unblocked_dmg))
                    if unblocked_thorns > 0:
                        sc -= unblocked_thorns * 16.0  # Play Block cards before hitting Thorns, and avoid multi-hit into unblocked Thorns!
                eff_atk_cost = player.get("energy", 1) if c.get("cost") == -1 else max(0, cost)
                if is_lethal_hit:
                    sc += 360.0 - eff_atk_cost * 35.0
                    if cid == "Feed":
                        sc += 250.0  # Feed lethal!
                    if lethal_incoming and eff_atk_cost >= 2 and (incoming_dmg - tm_atk_dmg - effective_block) >= player.get("currentHealth", 80):
                        if any(other.get("block", 0) > 0 and other.get("type") == "SKILL" for other in playable):
                            sc -= 180.0  # Block lethal damage from remaining enemies before spending >=2E!
                elif cid == "Feed" and not lethal_incoming and "Boss" not in room_cls:
                    sc -= 75.0  # Save Feed for the killing blow to gain +3/+4 Max HP!

            if sc > best_play_score:
                best_play_score = sc
                best_card = c
                best_target = t_idx

        if best_card and best_play_score > 0:
            log(f"Floor {floor} Turn {turn}: Playing [{best_card['index']}] {best_card['name']} (cost={best_card.get('costForTurn')}, target={best_target}, score={best_play_score:.1f})")
            play_card_api(best_card["index"], best_target, 0.35)
        else:
            log(f"Floor {floor} Turn {turn}: Done playing cards -> End Turn")
            end_turn_api(0.45)

    def step(self):
        st = get_state()
        if not st:
            time.sleep(0.3)
            return True

        mode = st.get("mode")
        if mode == "CHAR_SELECT":
            self.handle_main_menu(st)
            return True
        if mode == "DUNGEON_TRANSITION":
            click(960, 540, 0.8)
            return True

        d = st.get("dungeon", {})
        if d.get("isFadingIn") or d.get("isFadingOut"):
            time.sleep(0.25)
            return True

        scr = d.get("screen", "")
        floor = d.get("floorNum", 0)
        act = d.get("actNum", 1)
        room = st.get("room", {})
        r_cls = room.get("className", "")
        r_phase = room.get("phase", "")
        go = st.get("gameOver", {})

        # Check Victory or Death!
        if scr in ("VICTORY", "DEATH") or r_cls in ("VictoryRoom", "TrueVictoryRoom"):
            if go.get("isVictory") or scr == "VICTORY" or r_cls in ("VictoryRoom", "TrueVictoryRoom"):
                # In VictoryRoom (Spire Heart cutscene after Act 3 Boss), click event options until GameOverScreen shows
                ev_opts = st.get("event", {}).get("roomEventOptions", []) + st.get("event", {}).get("imageEventOptions", [])
                active_opts = [o for o in ev_opts if not o.get("isDisabled") and not o.get("pressed")]
                if active_opts:
                    self.maybe_screenshot("heart_scene", "98_spire_heart_cutscene.png")
                    click(active_opts[0]["hb"]["cx"], active_opts[0]["hb"]["cy"], 0.8)
                    return True
                if scr in ("VICTORY", "DEATH") and go.get("isVictory"):
                    time.sleep(1.5)
                    self.maybe_screenshot("victory_screen", "99_ironclad_victory_screen.png")
                    log("==========================================")
                    log("VICTORY! Ironclad beat Slay the Spire!")
                    log("==========================================")
                    return False
                click(960, 540, 0.8)
                return True
            else:
                # Player died on this attempt -> click Return to Menu and start a fresh run
                log(f"Run ended in defeat on Floor {floor} (Act {act}). Restarting run...")
                drb = go.get("deathReturnButton", {})
                if drb and drb.get("show") and drb.get("hb"):
                    click(drb["hb"]["cx"], drb["hb"]["cy"], 1.0)
                else:
                    click(960, 540, 0.8)
                self.screenshots_taken.clear()
                self.shop_visited_floors.clear()
                self.shop_clicks_per_floor.clear()
                self.potion_tries.clear()
                self.skipped_card_floors.clear()
                return True

        # Screen-specific handlers
        if scr == "GRID":
            self.handle_grid_select(st)
            return True
        if scr == "HAND_SELECT":
            self.handle_hand_select(st)
            return True
        if scr == "CARD_REWARD":
            self.handle_card_reward(st)
            return True
        if scr == "COMBAT_REWARD":
            self.handle_combat_reward(st)
            return True
        if scr == "BOSS_REWARD":
            self.handle_boss_relic(st)
            return True
        if (r_cls == "TreasureRoomBoss" and d.get("firstRoomChosen")) or (r_cls == "MonsterRoomBoss" and r_phase == "COMPLETE" and scr != "COMBAT_REWARD" and scr != "CARD_REWARD"):
            if scr == "MAP":
                ca = st.get("overlay", {}).get("cancel", {})
                if ca and not ca.get("isHidden"):
                    log(f"{r_cls}: Closing Map screen")
                    click(ca["hb"]["cx"], ca["hb"]["cy"], 0.5)
                    return True
            if r_cls == "TreasureRoomBoss":
                tr = st.get("treasure", {})
                if tr and not tr.get("isOpen") and tr.get("hb"):
                    log(f"Floor {floor} (TreasureRoomBoss): Opening Boss Chest")
                    click(tr["hb"]["cx"], tr["hb"]["cy"], 0.8)
                    return True
            pr = st.get("overlay", {}).get("proceed", {})
            if pr and not pr.get("isHidden"):
                log(f"Floor {floor} ({r_cls}): Clicking Proceed!")
                click(pr["hb"]["cx"], pr["hb"]["cy"], 1.0)
                return True
            time.sleep(0.3)
            return True
        if scr == "SHOP":
            self.handle_shop(st)
            return True
        if scr == "MAP":
            self.handle_map(st)
            return True

        # Combat check first (handles normal combat, Elite, Boss, and Event combat!)
        if r_phase == "COMBAT" and not room.get("isBattleOver"):
            self.handle_combat(st)
            return True

        # Room-specific handlers when no modal screen is up
        if (floor == 0 or r_cls == "NeowRoom" or r_phase == "EVENT" or r_cls == "EventRoom") and r_phase != "COMPLETE":
            if self.handle_event(st):
                return True

        if r_cls in ("TreasureRoom", "TreasureRoomBoss"):
            tr = st.get("treasure", {})
            pr = st.get("overlay", {}).get("proceed", {})
            if r_cls == "TreasureRoom" and has_relic(st.get("player", {}), "Cursed Key") and pr and not pr.get("isHidden"):
                log(f"Floor {floor} (TreasureRoom): Skipping chest due to Cursed Key -> Clicking Proceed")
                click(pr["hb"]["cx"], pr["hb"]["cy"], 0.6)
                return True
            if tr and not tr.get("isOpen") and tr.get("hb"):
                log(f"Floor {floor} ({r_cls}): Opening Chest")
                click(tr["hb"]["cx"], tr["hb"]["cy"], 0.7)
                return True
            if pr and not pr.get("isHidden"):
                log(f"Floor {floor} ({r_cls}): Clicking Proceed")
                click(pr["hb"]["cx"], pr["hb"]["cy"], 0.6)
                return True

        if r_cls == "RestRoom":
            self.handle_campfire(st)
            return True

        if r_cls == "ShopRoom":
            self.handle_shop(st)
            return True

        # If room is COMPLETE, click Proceed or open Map
        pr = st.get("overlay", {}).get("proceed", {})
        if pr and not pr.get("isHidden"):
            log(f"Floor {floor}: Clicking Proceed button")
            click(pr["hb"]["cx"], pr["hb"]["cy"], 0.5)
            return True

        if r_phase == "COMPLETE" or not d.get("firstRoomChosen"):
            self.handle_map(st)
            return True

        time.sleep(0.25)
        return True

def has_power_or_relic_barricade(player):
    return get_power_amt(player, "Barricade") > 0 or has_relic(player, "Calipers")

if __name__ == "__main__":
    log("Starting Ironclad AI Player...")
    bot = IroncladBot()
    while True:
        try:
            cont = bot.step()
            if not cont:
                break
        except KeyboardInterrupt:
            break
        except Exception as e:
            log(f"Step exception: {e}")
            time.sleep(0.5)
