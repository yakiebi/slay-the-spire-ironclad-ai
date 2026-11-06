import urllib.request
import urllib.parse
import json
import time

BASE = "http://127.0.0.1:17575"
ART_DIR = "C:/Users/User/.gemini/antigravity/brain/f94be6ae-41df-464f-bed4-1986c68037a3"

def get_state():
    with urllib.request.urlopen(f"{BASE}/state", timeout=5) as r:
        return json.loads(r.read().decode("utf-8"))

def click(x, y):
    url = f"{BASE}/action?cmd=click&x={int(round(x))}&y={int(round(y))}"
    with urllib.request.urlopen(url, timeout=5) as r:
        return json.loads(r.read().decode("utf-8"))

def screenshot(name):
    path = f"{ART_DIR}/{name}"
    url = f"{BASE}/screenshot?path={urllib.parse.quote(path)}"
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))

st = get_state()
mm = st.get("mainMenu", {})
print("Current screen:", mm.get("screen"))

if mm.get("screen") == "MAIN_MENU":
    for b in mm.get("buttons", []):
        if b["result"] == "PLAY":
            click(b["hb"]["cx"], b["hb"]["cy"])
            time.sleep(0.8)
            break
    st = get_state()
    mm = st.get("mainMenu", {})

if mm.get("screen") == "PANEL_MENU":
    for p in mm.get("panels", []):
        print("Panel:", p["result"], p["header"], p["hb"])
        if p["result"] == "PLAY_NORMAL":
            click(p["hb"]["cx"], p["hb"]["cy"])
            time.sleep(0.8)
            break
    st = get_state()
    mm = st.get("mainMenu", {})

print("Now screen:", mm.get("screen"))
if mm.get("screen") == "CHAR_SELECT":
    cs = mm.get("charSelect", {})
    for opt in cs.get("options", []):
        print("Option:", opt["chosenClass"], opt["name"], "selected:", opt["selected"])
        if opt["chosenClass"] == "IRONCLAD" and not opt["selected"]:
            click(opt["hb"]["cx"], opt["hb"]["cy"])
            time.sleep(0.6)
            break
    st = get_state()
    cs = st.get("mainMenu", {}).get("charSelect", {})
    if cs.get("isAscensionMode"):
        print("Disabling Ascension mode...")
        ahb = cs.get("ascensionHb")
        if ahb:
            click(ahb["cx"], ahb["cy"])
            time.sleep(0.5)
    st = get_state()
    cs = st.get("mainMenu", {}).get("charSelect", {})
    print("Ironclad selected! isAscensionMode:", cs.get("isAscensionMode"))
    sc = screenshot("01_char_select.png")
    print("Screenshot 01:", sc)
    cb = cs.get("confirmButton", {})
    if cb and not cb.get("isHidden"):
        print("Clicking Embark at", cb["hb"]["cx"], cb["hb"]["cy"])
        click(cb["hb"]["cx"], cb["hb"]["cy"])

# Wait for Neow room
for _ in range(30):
    time.sleep(0.5)
    st = get_state()
    if st.get("mode") == "GAMEPLAY":
        d = st.get("dungeon", {})
        ev = st.get("event", {})
        opts = ev.get("roomEventOptions", [])
        if not d.get("isFadingIn") and len(opts) > 0:
            print("Reached Neow! Floor:", d.get("floorNum"), "Options:", opts)
            sc2 = screenshot("02_neow.png")
            print("Screenshot 02:", sc2)
            break
