import network
import time

SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)   
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)

        # Wait until connected or timeout
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            print("Waiting for connection...")
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        print("✅ Connected to WiFi")
        print("IP address:", wlan.ifconfig()[0])
    else:
        print("❌ Failed to connect")

connect_wifi()
