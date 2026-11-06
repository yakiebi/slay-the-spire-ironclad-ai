# Slay the Spire — Autonomous Ironclad AI Experiment

An in-process Java instrumentation agent ([`StsObserverAgent.java`](observer/StsObserverAgent.java)) and autonomous Python decision engine ([`play_ironclad.py`](play_ironclad.py)) that plays **Slay the Spire** (*The Ironclad*, Standard / Ascension 0) purely through legitimate UI and render-thread interactions—evolving across **21 full runs** and **12 engineering iterations (`v1.0` → `v2.3`)** to achieve a **13m 21s Speed Climber Victory** (`Score: 667`, `Final HP: 71/93`).

---

## 🌐 Live Links

- **Interactive GitHub Pages Dashboard**: [https://yakiebi.github.io/slay-the-spire-ironclad-ai/](https://yakiebi.github.io/slay-the-spire-ironclad-ai/)
- **Live Google Spreadsheet (6 Tabs + Charts)**: [Slay the Spire — Ironclad AI Experiment Telemetry (21 Runs)](https://docs.google.com/spreadsheets/d/1QaTf-T1JtgsI-HPnWZleRwBCAV4ktXWXr7AtER40xrI/edit)
- **Download Multi-Tab Excel/Google Sheets Workbook**: [`data/slay_the_spire_ironclad_experiment.xlsx`](data/slay_the_spire_ironclad_experiment.xlsx)

---

## 🧠 How the Bot Was Built (Methodology & System Architecture)

Rather than relying on fragile computer-vision screen scraping (OCR/template matching) or requiring third-party mod loaders (*ModTheSpire* / *BaseMod* / *CommunicationMod*), we built a **zero-dependency, two-layer architecture** that works directly with an unmodified Steam installation of *Slay the Spire*:

```
┌────────────────────────────────────────────────────────────────────────────┐
│               Slay the Spire JVM Process (desktop-1.0.jar)                 │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  1. In-Process Java Agent (-javaagent:observer/sts_observer.jar)     │  │
│  │     • Attaches via premain() before CardCrawlGame.main() starts      │  │
│  │     • Hosts embedded HTTP Server on http://127.0.0.1:17575           │  │
│  │     • /state      -> Serializes live JVM game objects to JSON        │  │
│  │     • /action     -> Queues UI & combat actions on LibGDX thread     │  │
│  │     • /screenshot -> Captures 1080p OpenGL framebuffer PNGs          │  │
│  └──────────────────▲─────────────────────────────────┬─────────────────┘  │
└─────────────────────┼─────────────────────────────────┼────────────────────┘
                      │ HTTP GET /action                │ HTTP GET /state (JSON)
                      │                                 ▼
┌─────────────────────┴──────────────────────────────────────────────────────┐
│               2. Python Decision Engine (play_ironclad.py)                 │
│                                                                            │
│  • Screen Router (step): Main Menu -> Neow -> Map -> Combat -> Rewards     │
│  • Card Evaluator (evaluate_card_for_deck): Base tier + synergy bonuses    │
│  • 3-Floor Lookahead Map Router (handle_map): HP/Gold/Act-aware pathing    │
│  • 5-Stage Combat Planner (handle_combat): Setup -> Powers -> Debuffs ->   │
│    Urgency-Weighted Block -> Universal Lethal & Thorns/Intangible Checks   │
└────────────────────────────────────────────────────────────────────────────┘
```

### 1. Layer 1: In-Process Java Agent (`observer/StsObserverAgent.java`)
- **JVM Attachment (`premain`)**: Loaded via the standard JVM flag `-javaagent:observer/sts_observer.jar`. No bytecode patching or `.jar` modification is needed.
- **Exact State Introspection (`/state`)**: Reads live references from `CardCrawlGame`, `AbstractDungeon`, `AbstractPlayer`, `AbstractRoom`, and active screen objects (`GridCardSelectScreen`, `HandCardSelectScreen`, `CombatRewardScreen`, `CardRewardScreen`, `BossRelicSelectScreen`, `ShopScreen`, `DungeonMapScreen`) and serializes exact HP, block, energy, monster intents (`intentDmg`, `intentMultiAmt`), powers/debuffs, cards in hand (`canUse`, `costForTurn`, `damage`, `block`), relics, potions, and screen hitboxes (`cx`, `cy`, `w`, `h`).
- **Thread-Safe Action Execution (`/action`)**: Because LibGDX's OpenGL context and *Slay the Spire*'s `GameActionManager` are single-threaded, all actions (`play_card`, `end_turn`, `click`, `hand_select`, `scroll`, `key`) are dispatched inside `Gdx.app.postRunnable(...)` so they execute deterministically on the main render loop without race conditions.
- **Rules-Compliant Gameplay**: The agent never alters HP, gold, card values, or RNG seeds. Cards are queued into `AbstractDungeon.actionManager.cardQueue.add(new CardQueueItem(card, monster))`—the exact same queue populated when a human drags and releases a card.

### 2. Layer 2: Iterative Failure-Driven Engineering (`play_ironclad.py`)
We developed the Python bot through **12 closed-loop engineering iterations (`v1.0` → `v2.3`)** across **21 full runs**:
1. **Run the bot autonomously** and record full combat/screen telemetry logs (`run_history.log` and Slay the Spire's `.run` JSON files).
2. **Diagnose the exact bottleneck** whenever a run lost or got stuck on an unfamiliar UI modal (e.g., `GremlinMatchGame` 4x3 card grid, `Astrolabe` multi-card selection, `PotionPopUp.targetMode`, `Gambling Chip` optional discard).
3. **Encode domain-specific counter-heuristics** for Bosses and Elites:
   - **Slime Boss (Floor 16)**: Added a `+250` priority spike to attacks that push `Slime Boss` to `<= 70 HP`, interrupting its `35`-damage *Slam* with an immediate split.
   - **Awakened One (Floor 50)**: Added a `Curiosity` check that suppresses non-essential Powers during Phase 1 so the boss doesn't gain `+2 Strength` per Power played.
   - **Nemesis & Spiker (Act 3)**: Added `Intangible` awareness (capping expected attack damage at `1` per hit and prioritizing Block over 2-cost attacks) and `Thorns` self-damage protection.
   - **Time Eater (Floor 50)**: Built `Time Warp` counter discipline (stopping non-Power plays at `6..8` when all incoming damage is blocked so the next turn has `4..6` plays, while pushing through `9..11` so the counter resets to `0/12` for the next turn) and `Haste` turn conservation (never wasting attacks or debuffs when `Time Eater` intents `BUFF` below `50% HP`).

---

## 🚀 How to Install & Run the Bot Yourself

### Prerequisites
1. **Slay the Spire** installed via Steam (default path: `C:\Program Files (x86)\Steam\steamapps\common\SlayTheSpire`).
   - *Note*: Steam's *Slay the Spire* comes bundled with its own Java 8 runtime (`jre\bin\java.exe`), so you do **not** even need Java installed globally to run the prebuilt `sts_observer.jar`!
2. **Python 3.8+** (uses only the Python standard library: `urllib.request`, `json`, `time`, `re`, `os`—no `pip install` required to run the bot!).

### Step 1: Clone the Repository
```powershell
git clone https://github.com/yakiebi/slay-the-spire-ironclad-ai.git
cd slay-the-spire-ironclad-ai
```

### Step 2: Launch *Slay the Spire* with the Observer Agent Attached
Make sure Steam is running, then either double-click **`launch_sts_with_agent.bat`** or run:

```powershell
# If Slay the Spire is in the default Steam folder:
.\launch_sts_with_agent.bat

# Or if installed in a custom SteamLibrary folder:
$env:STS_DIR = "D:\SteamLibrary\steamapps\common\SlayTheSpire"
.\launch_sts_with_agent.bat
```

*(Under the hood, this runs `.\jre\bin\java.exe -Xmx1G -javaagent:...\observer\sts_observer.jar -jar desktop-1.0.jar` and starts the local bridge on `http://127.0.0.1:17575`.)*

You can verify the bridge is live at any time by visiting [http://127.0.0.1:17575/state](http://127.0.0.1:17575/state) in your browser.

### Step 3: Start the Autonomous Ironclad Bot
In a second terminal window, run:

```powershell
python play_ironclad.py
```

The bot will automatically navigate from the Main Menu (or resume an in-progress run), select **The Ironclad**, take Neow's Blessing, and play through Acts 1–3 in real time while printing turn-by-turn decisions to the console and `run_history.log`.

---

## 🛠️ How to Edit, Customize, or Train Your Own Bot

### 1. Tuning Card Draft & Shop Priorities (`play_ironclad.py`)
Open [`play_ironclad.py`](play_ironclad.py) and look at:
- **`CARD_SCORES` (lines 70–160)**: Base tier values (`0–100`) for every Ironclad and Colorless card. Increase a card's score to draft it more aggressively, or lower it below `56` (the skip threshold) to skip it unless upgraded/synergistic.
- **`evaluate_card_for_deck(card, state)` (lines 195–275)**: Dynamic synergy adjustments based on your current `masterDeck` and `relics`. For example, you can add custom rules for a **Barricade + Entrench + Body Slam** archetype or a **Rupture + Hemokinesis / Combust** self-damage archetype:

```python
# Example: Boost Entrench & Impervious when Barricade or Calipers is in the deck/relics
if cid in ("Entrench", "Impervious", "Body Slam"):
    if any(c.get("id") == "Barricade" for c in deck) or has_relic(player, "Calipers"):
        score += 25
```

### 2. Modifying Combat Card Sequencing (`handle_combat` in `play_ironclad.py`)
In [`play_ironclad.py`](play_ironclad.py), `handle_combat(self, st)` loops over every playable card in `player["hand"]` (`canUse == True`) and computes a priority score `sc`:
- **To add a new boss/elite counter-strategy**, inspect `alive_monsters` (`id`, `name`, `currentHealth`, `currentBlock`, `intent`, `intentDmg`, `powers`) and adjust `sc` or `continue` to skip a card.
- **To change how aggressively the bot blocks vs. attacks**, adjust `urgency_bonus` and `base_blk_sc` in the `# 4. Block cards` section (around line 1370).

### 3. Modifying Map Routing (`handle_map` in `play_ironclad.py`)
`score_node(n, depth)` inside `handle_map` evaluates a **3-floor lookahead tree** (`s += 0.65 * max(child_scores)`) over the dungeon map nodes (`R` Rest, `E` Elite, `$` Shop, `T` Treasure, `?` Event, `M` Monster). You can edit node weights to hunt more Elites (e.g., for High Ascension or Black Star runs) or route toward the Burning Elite (`n.get("hasEmeraldKey") == True`) for Act 4 Heart runs!

### 4. Building Your Own RL / Imitation Learning / LLM Agent Using the HTTP API
Because `StsObserverAgent` exposes a language-agnostic HTTP JSON API on `http://127.0.0.1:17575`, you can write your own agent in **Python (PyTorch / Gymnasium / Stable-Baselines3)**, **TypeScript**, **Rust**, or **Go**, or connect an **LLM agent**:

| Endpoint | Method | Parameters / Description |
| :--- | :---: | :--- |
| `/state` | `GET` | Returns full JSON snapshot of `mode`, `dungeon`, `room`, `actionManager`, `player` (HP, energy, hand, deck, relics, potions, powers), `monsters` (HP, intent, powers), `overlay`, `map`, `shop`, `event`, `combatRewards`, `cardReward`, `bossRelics`, `gridSelect`, `handSelect`, `gameOver`. |
| `/action?cmd=play_card&index=<i>&target=<m>` | `GET` | Plays hand card at index `i` targeting monster index `m` (`-1` for self/AoE/untargeted cards). |
| `/action?cmd=end_turn` | `GET` | Clicks the End Turn button (`AbstractDungeon.overlayMenu.endTurnButton.disable(true)`). |
| `/action?cmd=click&x=<cx>&y=<cy>` | `GET` | Moves cursor to `(x, y)` in 1920x1080 space and performs a left-click on the LibGDX render thread. |
| `/action?cmd=hand_select&index=<i>` | `GET` | Selects card `i` in `HandCardSelectScreen` (Armaments, True Grit, Dual Wield, Gambling Chip). |
| `/action?cmd=scroll&dir=<up\|down>&amount=<n>` | `GET` | Scrolls the Dungeon Map or Grid Select screen. |
| `/action?cmd=key&key=<ESC\|RETURN\|SPACE>` | `GET` | Presses a keyboard key inside LibGDX. |
| `/screenshot?path=<abs_path.png>` | `GET` | Captures a 1920x1080 PNG screenshot directly from the OpenGL framebuffer. |

#### Minimal Custom Agent Template (Python)
```python
import urllib.request, json, time

BASE = "http://127.0.0.1:17575"

def get_state():
    with urllib.request.urlopen(f"{BASE}/state") as r:
        return json.loads(r.read().decode("utf-8"))

def act(query):
    with urllib.request.urlopen(f"{BASE}/action?{query}") as r:
        return json.loads(r.read().decode("utf-8"))

while True:
    state = get_state()
    if state["room"].get("phase") == "COMBAT" and state["actionManager"].get("phase") == "WAITING_ON_USER":
        playable = [c for c in state["player"]["hand"] if c["canUse"]]
        if playable:
            card = playable[0]
            target = 0 if card["target"] in ("ENEMY", "SELF_AND_ENEMY") else -1
            act(f"cmd=play_card&index={card['index']}&target={target}")
        else:
            act("cmd=end_turn")
    time.sleep(0.4)
```

### 5. Recompiling the Java Agent (`observer/StsObserverAgent.java`)
If you add new fields to `/state` or new commands to `/action` in [`observer/StsObserverAgent.java`](observer/StsObserverAgent.java), recompile `observer/sts_observer.jar` using JDK 8+:

```powershell
.\build_observer_jar.bat
```

### 6. Regenerating the Telemetry Spreadsheets & GitHub Pages Data
After running your own experiments, run [`generate_experiment_assets.py`](generate_experiment_assets.py) to parse all `.run` files from your *Slay the Spire* `runs\IRONCLAD` folder and automatically update [`data/`](data/), [`docs/data/`](docs/data/), and [`docs/data.js`](docs/data.js):

```powershell
python generate_experiment_assets.py
```

---

## 📊 Google Sheets & CSV Spreadsheets

- **Live Google Spreadsheet (in Google Drive)**: [Slay the Spire — Ironclad AI Experiment Telemetry (21 Runs)](https://docs.google.com/spreadsheets/d/1QaTf-T1JtgsI-HPnWZleRwBCAV4ktXWXr7AtER40xrI/edit)
- **Multi-Tab OpenXML Workbook (`.xlsx`)**: [`data/slay_the_spire_ironclad_experiment.xlsx`](data/slay_the_spire_ironclad_experiment.xlsx)
- **Individual CSV Datasets**:
  - [`data/runs_summary.csv`](data/runs_summary.csv) — All 21 runs
  - [`data/card_pick_rates.csv`](data/card_pick_rates.csv) — All 69 cards offered across 1,018 reward slots
  - [`data/relics_obtained.csv`](data/relics_obtained.csv) — All 63 relics obtained/offered
  - [`data/iterations_changelog.csv`](data/iterations_changelog.csv) — All 12 AI engineering iterations (`v1.0` → `v2.3`)
  - [`data/enemy_damage_summary.csv`](data/enemy_damage_summary.csv) — Aggregated combat difficulty across 37 enemy groups
  - [`data/combat_encounters.csv`](data/combat_encounters.csv) — All 354 individual combat encounters

---

## 🏆 Experiment Summary Metrics

| Metric | Value | Notes |
| :--- | :--- | :--- |
| **Total Runs** | `21` | Chronological runs from `v1.0` baseline to `v2.3` victory |
| **Total Playtime** | `4h 33m 50s` (`16,430s`) | Avg `13m 02s` (`782s`) per run |
| **Total Combats Fought** | `354` | Across Acts 1, 2, and 3 |
| **Total Cards Offered / Picked** | `326 / 1,018` | `32.0%` per-card selection rate across 340+ reward screens |
| **Act 3 Reach Rate (Phase 5, Runs #18–#21)** | `100%` (`4 / 4`) | Reached Floor 46, 50, 50, and 51 (Victory!) |
| **Floor 50 Boss Reach Rate (Phase 5)** | `75%` (`3 / 4`) | `Time Eater` (x2) and `Donu and Deca` (Victory!) |
| **Winning Run (#21) Time & Score** | `13m 21s` (`801s`) • `667 pts` | Unlocked `SPEED_CLIMBER`, `SHAPES`, and `RUBY` |
