# ESP32 → MQTT → Node-RED → InfluxDB → Grafana Dashboard

This project demonstrates a complete IoT data pipeline using an **ESP32** running **MicroPython**, sending random sensor values via **MQTT** to **Node-RED**, which stores the data in **InfluxDB** and visualizes it in **Grafana**.

---

## 🧭 Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [1) Flash & run ESP32 code (MicroPython)](#1-flash--run-esp32-code-micropython)
- [2) Node-RED flow (MQTT → InfluxDB)](#2-node-red-flow-mqtt--influxdb)
- [3) InfluxDB 1.x setup & quick test](#3-influxdb-1x-setup--quick-test)
- [4) Grafana: add data source & dashboard](#4-grafana-add-data-source--dashboard)
- [5) Verification](#5-verification)
- [6) Troubleshooting](#6-troubleshooting)

  ESP32 (MicroPython)
    └── publishes random ints → MQTT topic: /aupp/esp32/random
          └── MQTT broker (test.mosquitto.org:1883)
                └── Node-RED (MQTT In → Function → InfluxDB Out)
                      └── InfluxDB (measurement: random, field: value, tag: device)
                            └── Grafana (InfluxQL queries + auto refresh)

