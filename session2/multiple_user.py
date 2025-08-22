
import network, time, urequests, json
from machine import Pin, reset

# ---------- USER CONFIG ----------
WIFI_SSID     = "project"
WIFI_PASSWORD = "12345678"

BOT_TOKEN     = "8275338754:AAFOwRHBPpAl883Lp8H-KOK8sQdDILPA52M"
RELAY_PIN = 2
RELAY_ACTIVE_LOW = False
POLL_TIMEOUT_S = 20
DEBUG = True
ALLOWLIST_FILE = "allowlist.txt"   # persists chat IDs across reboots
ADMIN_FILE     = "admin.txt"       # persists admin chat ID
API = "https://api.telegram.org/bot" + BOT_TOKEN
relay = Pin(RELAY_PIN, Pin.OUT)

def log(*a):
    if DEBUG: print(*a)

# --- URL encoding (simple) ---
def urlencode(d):
    parts = []
    for k, v in d.items():
        s = str(v)
        s = (s.replace("%", "%25").replace(" ", "%20").replace("\n", "%0A")
               .replace("&", "%26").replace("?", "%3F").replace("=", "%3D"))
        parts.append(str(k)+"="+s)
    return "&".join(parts)

# --- Relay helpers ---
def relay_on():  relay.value(0 if RELAY_ACTIVE_LOW else 1)
def relay_off(): relay.value(1 if RELAY_ACTIVE_LOW else 0)
def relay_is_on(): return (relay.value()==0) if RELAY_ACTIVE_LOW else (relay.value()==1)

# --- Wi-Fi ---
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        t0 = time.time()
        while not wlan.isconnected():
            if time.time()-t0 > 25:
                raise RuntimeError("Wi-Fi connect timeout")
            time.sleep(0.25)
    print("Wi-Fi OK:", wlan.ifconfig())
    return wlan

# --- Allow-list & Admin persistence ---
def load_ids(path):
    try:
        with open(path, "r") as f:
            ids = set(int(line.strip()) for line in f if line.strip())
        return ids
    except:
        return set()

def save_ids(path, ids):
    try:
        with open(path, "w") as f:
            for cid in sorted(ids):
                f.write(str(cid)+"\n")
    except Exception as e:
        print("save_ids error:", e)

def load_admin():
    try:
        with open(ADMIN_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return None

def save_admin(chat_id):
    try:
        with open(ADMIN_FILE, "w") as f:
            f.write(str(chat_id))
    except Exception as e:
        print("save_admin error:", e)

ALLOWED = load_ids(ALLOWLIST_FILE)
ADMIN_CHAT_ID = load_admin()

# --- Telegram API ---
def send_message(chat_id, text):
    try:
        url = API + "/sendMessage?" + urlencode({"chat_id": chat_id, "text": text})
        r = urequests.get(url)
        _ = r.text; r.close()
        log("→ sent to", chat_id)
    except Exception as e:
        print("send_message error:", e)

def broadcast(text):
    for cid in list(ALLOWED):
        send_message(cid, text)

def get_updates(offset=None, timeout=POLL_TIMEOUT_S):
    qs = {"timeout": timeout}
    if offset is not None:
        qs["offset"] = offset
    url = API + "/getUpdates?" + urlencode(qs)
    try:
        r = urequests.get(url)
        data = r.json(); r.close()
        if not data.get("ok"):
            print("getUpdates not ok:", data)
            return []
        return data.get("result", [])
    except Exception as e:
        print("get_updates error:", e)
        return []

def whoami(cid): return "Your chat id: {}".format(cid)

HELP = (
    "Commands:\n"
    "/start – help\n"
    "/status – current state\n"
    "/on, /off – control relay\n"
    "/whoami – show your chat id\n"
    "Admin only: /allow <id>, /revoke <id>, /list"
)

def is_admin(cid): return ADMIN_CHAT_ID is not None and cid == ADMIN_CHAT_ID

def ensure_admin_and_allow(first_cid):
    global ADMIN_CHAT_ID, ALLOWED
    if ADMIN_CHAT_ID is None:
        ADMIN_CHAT_ID = first_cid
        save_admin(ADMIN_CHAT_ID)
        ALLOWED.add(first_cid)
        save_ids(ALLOWLIST_FILE, ALLOWED)
        send_message(first_cid, "You are now ADMIN and authorized.")
        log("Admin learned:", ADMIN_CHAT_ID)

def add_allowed(target_id):
    ALLOWED.add(target_id); save_ids(ALLOWLIST_FILE, ALLOWED)

def remove_allowed(target_id):
    if target_id in ALLOWED:
        ALLOWED.remove(target_id); save_ids(ALLOWLIST_FILE, ALLOWED)

def handle_cmd(chat_id, text):
    t = (text or "").strip()
    tl = t.lower()

    # admin bootstrap
    ensure_admin_and_allow(chat_id)

    # gate
    if chat_id not in ALLOWED and not is_admin(chat_id):
        send_message(chat_id, "Not authorized. Ask admin to /allow your id.\n"+whoami(chat_id))
        return

    if tl in ("/start", "/help", "help"):
        send_message(chat_id, HELP)
    elif tl in ("/whoami", "whoami"):
        send_message(chat_id, whoami(chat_id))
    elif tl in ("/status", "status"):
        send_message(chat_id, "Relay is " + ("ON" if relay_is_on() else "OFF"))
    elif tl in ("/on", "on"):
        relay_on()
        broadcast("Relay: ON (by {})".format(chat_id))
    elif tl in ("/off", "off"):
        relay_off()
        broadcast("Relay: OFF (by {})".format(chat_id))
    elif tl.startswith("/allow") and is_admin(chat_id):
        parts = tl.split()
        if len(parts)==2:
            try:
                new_id = int(parts[1])
                add_allowed(new_id)
                send_message(chat_id, "Allowed: {}".format(new_id))
                send_message(new_id, "You have been authorized.")
            except:
                send_message(chat_id, "Usage: /allow <chat_id>")
        else:
            send_message(chat_id, "Usage: /allow <chat_id>")
    elif tl.startswith("/revoke") and is_admin(chat_id):
        parts = tl.split()
        if len(parts)==2:
            try:
                rid = int(parts[1])
                remove_allowed(rid)
                send_message(chat_id, "Revoked: {}".format(rid))
            except:
                send_message(chat_id, "Usage: /revoke <chat_id>")
        else:
            send_message(chat_id, "Usage: /revoke <chat_id>")
    elif tl == "/list" and is_admin(chat_id):
        send_message(chat_id, "Allowed: " + ", ".join(str(i) for i in sorted(ALLOWED)))
        if ADMIN_CHAT_ID is not None:
            send_message(chat_id, "Admin: {}".format(ADMIN_CHAT_ID))
    else:
        send_message(chat_id, "Unknown. Type /help")

def main():
    connect_wifi()
    relay_off()

    # drain old updates
    last_id = None
    old = get_updates(timeout=1)
    if old:
        last_id = old[-1]["update_id"]

    print("Bot running. Waiting for commands…")
    while True:
        try:
            if not network.WLAN(network.STA_IF).isconnected():
                connect_wifi()
        except:
            pass

        updates = get_updates(offset=(last_id + 1) if last_id is not None else None)
        for u in updates:
            last_id = u["update_id"]
            msg = u.get("message") or u.get("edited_message")
            if not msg: continue
            cid = msg["chat"]["id"]
            txt = msg.get("text", "")
            log("From", cid, ":", txt)
            handle_cmd(cid, txt)

        time.sleep(0.4)

try:
    main()
except Exception as e:
    print("Fatal error:", e)
    time.sleep(5)
    reset()