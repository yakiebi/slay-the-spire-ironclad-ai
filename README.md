# Slay the Spire — Autonomous Ironclad AI Experiment

An in-process Java instrumentation agent (`StsObserverAgent`) and autonomous Python decision engine (`play_ironclad.py`) that plays **Slay the Spire** (The Ironclad) purely through legitimate UI/render-thread actions, evolving across **21 full runs** and **12 engineering iterations (`v1.0` → `v2.3`)** to achieve a **13m 21s Speed Climber Victory** (`Score: 667`, `Final HP: 71/93`).

---

## 🌐 GitHub Pages Interactive Dashboard

- **Live GitHub Pages URL**: [https://yakiebi.github.io/slay-the-spire-ironclad-ai/](https://yakiebi.github.io/slay-the-spire-ironclad-ai/)

The full interactive experiment site (with Chart.js visualizations, sortable/filterable Google Sheets tables, one-click TSV clipboard export, and 1080p OpenGL screenshots) is located in [`docs/index.html`](docs/index.html).

- **Local Preview**: Open [`docs/index.html`](docs/index.html) directly in any browser (zero server required), or run `python -m http.server 8080 --directory docs`.
- **GitHub Pages Deployment**: Included in [`.github/workflows/pages.yml`](.github/workflows/pages.yml) (automatically deploys `./docs` on push to `main`/`master`).

---

## 📊 Google Sheets & CSV Spreadsheets

- **Live Google Spreadsheet (in Google Drive)**: [Slay the Spire — Ironclad AI Experiment Telemetry (21 Runs)](https://docs.google.com/spreadsheets/d/1QaTf-T1JtgsI-HPnWZleRwBCAV4ktXWXr7AtER40xrI/edit)

All telemetry extracted from the 21 `.run` history files is also available in [`data/`](data/) and [`docs/data/`](docs/data/):

1. **[`slay_the_spire_ironclad_experiment.xlsx`](data/slay_the_spire_ironclad_experiment.xlsx)** — Multi-tab OpenXML workbook ready to upload directly to **Google Sheets** (`File → Import → Upload`), containing all 6 tabs below with frozen headers:
   - **Tab 1 — [`runs_summary.csv`](data/runs_summary.csv)**: All 21 runs (`Run_Number`, `Iteration`, `Phase`, `Floor_Reached`, `Outcome`, `Killed_By`, `Playtime_Sec`, `Playtime_MMSS`, `Score`, `Boss_Relics`, `Cards_Picked`, `Cards_Skipped`, `Card_Pick_Rate_Pct`, `Total_Combat_Damage_Taken`).
   - **Tab 2 — [`card_pick_rates.csv`](data/card_pick_rates.csv)**: All 69 cards offered across 1,018 card reward slots (`Card_Name`, `Bot_Base_Score`, `Times_Offered`, `Times_Picked`, `Times_Passed`, `Pick_Rate_Pct`, `Upgraded_Picks`, `Shop_Purchases`, `Copies_In_Victory_Deck`).
   - **Tab 3 — [`relics_obtained.csv`](data/relics_obtained.csv)**: All 63 relics encountered/obtained (`Relic_Name`, `Category`, `Runs_Obtained`, `Run_Presence_Pct`, `Avg_Floor_Obtained`, `Boss_Pick_Rate_Pct`, `In_Winning_Run`).
   - **Tab 4 — [`iterations_changelog.csv`](data/iterations_changelog.csv)**: All 12 AI engineering iterations (`v1.0` → `v2.3`), bottleneck diagnosed, and strategy changes implemented.
   - **Tab 5 — [`enemy_damage_summary.csv`](data/enemy_damage_summary.csv)**: Aggregated combat difficulty across 37 enemy types (`Encounters_Fought`, `Avg_Damage_Taken`, `Max_Damage_Taken`, `Avg_Turns`).
   - **Tab 6 — [`combat_encounters.csv`](data/combat_encounters.csv)**: Every one of the 354 individual combat encounters fought across all 21 runs.

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

---

## 🛠️ Repository Structure

- [`observer/StsObserverAgent.java`](observer/StsObserverAgent.java) — In-process Java agent attached via `-javaagent:sts_observer.jar`, exposing `/state`, `/action`, and `/screenshot` on `http://127.0.0.1:17575`.
- [`play_ironclad.py`](play_ironclad.py) — Autonomous Ironclad AI player (card evaluation, combat turn planner, 3-floor lookahead map router, event/shop/campfire state machine).
- [`generate_experiment_assets.py`](generate_experiment_assets.py) — Telemetry parser that processes `.run` files into `.csv`, `.xlsx`, and `docs/data.js`.
- [`docs/`](docs/) — Self-contained GitHub Pages static web application.
- [`data/`](data/) — Google Sheets `.xlsx` workbook and `.csv` datasets.
