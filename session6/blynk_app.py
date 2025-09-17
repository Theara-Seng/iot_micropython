import network, time, machine, ujson
import urequests as requests
import dht

# ---------- CONFIG ----------
WIFI_SSID = "Robotic WIFI"
WIFI_PASS = "rbtWIFI@2025"

BLYNK_TOKEN = "-qYNTyr2EtlxX-4XzCyCSOa45hTo0qN7"            # Device token from Blynk Console → Devices
BLYNK_API   = "http://blynk.cloud/external/api"  # use http to avoid SSL issues on older builds

LED_PIN = 2                 # try 2; if no onboard LED, use pin 5 or wire an external LED + 220Ω → GND
LED_ACTIVE_HIGH = True     # many ESP32 onboard LEDs are active-LOW (False)

DHT_PIN = 4
USE_DHT11 = True            # set False if using DHT22

POLL_BTN_MS = 400           # poll V0
PUSH_TEMP_MS = 3000         # push V1

# ---------- HW ----------
led = machine.Pin(LED_PIN, machine.Pin.OUT)
def LED_ON():  led.value(1 if LED_ACTIVE_HIGH else 0)
def LED_OFF(): led.value(0 if LED_ACTIVE_HIGH else 1)

sensor = dht.DHT11(machine.Pin(DHT_PIN)) if USE_DHT11 else dht.DHT22(machine.Pin(DHT_PIN))

# ---------- Wi-Fi ----------
def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        t0 = time.ticks_ms()
        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), t0) > 15000:
                raise OSError("Wi-Fi timeout")
            time.sleep_ms(200)
    print("Wi-Fi:", wlan.ifconfig())
    return wlan

def wifi_ensure(wlan):
    if not wlan.isconnected():
        try: wlan.disconnect()
        except: pass
        wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PASS)
        t0 = time.ticks_ms()
        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), t0) > 15000:
                print("Reconn timeout; will retry…")
                break
            time.sleep_ms(200)
        if wlan.isconnected():
            print("Wi-Fi reconnected:", wlan.ifconfig())
    return wlan.isconnected()

# ---------- Blynk REST ----------
def _safe_close(r):
    try: r.close()
    except: pass

def blynk_get_v0():
    """Return 0/1 (int) or None on error. Accepts 1, 0, '1', '0', ['1'], [1], true/false."""
    url = f"{BLYNK_API}/get?token={BLYNK_TOKEN}&V0"
    r = None
    try:
        r = requests.get(url)
        if r.status_code != 200:
            print("GET V0 HTTP", r.status_code, r.text)
            return None
        txt = r.text.strip()
        # Try JSON first
        try:
            obj = ujson.loads(txt)
        except Exception:
            obj = txt  # keep raw

        # Normalize to a single value
        if isinstance(obj, list) and obj:
            val = obj[0]
        else:
            val = obj

        # Coerce to int 0/1
        if isinstance(val, bool):
            return 1 if val else 0
        if isinstance(val, (int, float)):
            return 1 if int(val) != 0 else 0
        if isinstance(val, str):
            s = val.strip().strip('"').lower()
            if s in ("1", "true", "on"):  return 1
            if s in ("0", "false", "off"): return 0
            # last resort: try int()
            try:
                return 1 if int(s) != 0 else 0
            except:
                print("GET V0 parse err:", txt)
                return None
        print("GET V0 unknown type:", type(val), val)
        return None
    except Exception as e:
        print("GET V0 error:", e)
        return None
    finally:
        if r: _safe_close(r)

def blynk_update_v1(temp_c):
    url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&v1={temp_c:.1f}"
    r = None
    try:
        r = requests.get(url)
        if r.status_code != 200:
            print("UPDATE V1 HTTP", r.status_code, r.text)
    except Exception as e:
        print("UPDATE V1 error:", e)
    finally:
        if r: _safe_close(r)

# ---------- Sensor ----------
def read_temp_c():
    for _ in range(3):
        try:
            sensor.measure()
            t = sensor.temperature()
            if t is not None:
                return t
        except:
            time.sleep_ms(250)
    return None

# ---------- Main ----------
def main():
    wlan = wifi_connect()



    next_btn  = time.ticks_ms()
    next_push = time.ticks_ms()
    last_v0   = None

    print("Running… V0→LED, V1=temp(°C)")
    while True:
        wifi_ensure(wlan)

        now = time.ticks_ms()

        # 1) Poll V0
        if time.ticks_diff(now, next_btn) >= 0:
            v0 = blynk_get_v0()
            if v0 is not None:
                print("V0 (cloud):", v0)
                if v0 != last_v0:
                    if v0 == 1: LED_ON()
                    else:       LED_OFF()
                    last_v0 = v0
            next_btn = time.ticks_add(now, POLL_BTN_MS)

        # 2) Push temperature to V1
        if time.ticks_diff(now, next_push) >= 0:
            t = read_temp_c()
            if t is not None:
                print("Temp:", "{:.1f}°C".format(t))
                blynk_update_v1(t)
            else:
                print("Temp read failed")
            next_push = time.ticks_add(now, PUSH_TEMP_MS)

        time.sleep_ms(40)

try:
    main()
except Exception as e:
    print("Fatal:", e)
 