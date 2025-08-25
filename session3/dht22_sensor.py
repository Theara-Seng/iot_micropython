import machine
import dht
import time

# Pin configuration
sensor = dht.DHT22(machine.Pin(4))   # GPIO4

while True:
    try:
        sensor.measure()  # Trigger measurement
        temp = sensor.temperature()   # Celsius
        hum = sensor.humidity()       # %
        
        # Print values
        print("Temperature: {:.2f}°C".format(temp))
        print("Humidity: {:.2f}%".format(hum))
        print("-" * 30)
        
    except OSError as e:
        print("Failed to read sensor:", e)
    
    time.sleep(2)  # Wait 2 seconds (required for DHT22)
