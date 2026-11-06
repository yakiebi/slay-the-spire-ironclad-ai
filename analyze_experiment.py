import glob
import json
import os
import datetime

runs_dir = r"C:\Program Files (x86)\Steam\steamapps\common\SlayTheSpire\runs\IRONCLAD"
files = sorted(glob.glob(os.path.join(runs_dir, "*.run")), key=os.path.getmtime)
print(f"Total .run files: {len(files)}")
for i, f in enumerate(files, 1):
    with open(f, "r", encoding="utf-8") as fp:
        d = json.load(fp)
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M:%S")
    fl = d.get("floor_reached", 0)
    vic = d.get("victory", False)
    pt = d.get("playtime", 0)
    sc = d.get("score", 0)
    kb = d.get("killed_by", "NONE (VICTORY!)" if vic else "Abandon/Reset")
    nb = d.get("neow_bonus", "NONE")
    br = [b.get("picked", "None") for b in d.get("boss_relics", [])]
    print(f"{i:2d}. {os.path.basename(f)} | {mtime} | Floor: {fl:2d} | Vic: {str(vic):5s} | Time: {pt:4d}s | Score: {sc:3d} | KilledBy: {kb:22s} | Neow: {nb:24s} | BossRelics: {br}")
