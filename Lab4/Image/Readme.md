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

## ESP32 (MicroPython)

└── publishes random ints → MQTT topic: /aupp/esp32/random

└── MQTT broker (test.mosquitto.org:1883)

└── Node-RED (MQTT In → Function → InfluxDB Out)

└── InfluxDB (measurement: random, field: value, tag: device)

└── Grafana (InfluxQL queries + auto refresh)

## ⚙️ Prerequisites

### Hardware
- ESP32 board (any variant supporting MicroPython)

### Software
- [MicroPython](https://micropython.org/download/esp32/) flashed on ESP32  (Upload scripts using **Thonny**, **mpremote**, or **ampy**)
- [Node-RED](https://nodered.org/) Local automation server. Accessible at: [http://localhost:1880](http://localhost:1880)
- [InfluxDB 1.x](https://docs.influxdata.com/influxdb/v1.8/introduction/). Time-series database Running at: [http://127.0.0.1:8086 (http://127.0.0.1:8086)
- [Grafana](https://grafana.com/grafana/download) — Visualization dashboard. Accessible at: [http://localhost:3000](http://localhost:3000)

### Optional Tools
- [MQTT Explorer](https://mqtt-explorer.com/) — inspect and debug MQTT topics

### ⚙️ Installing Node-RED (Local Setup)

Node-RED is a flow-based tool for wiring together hardware, APIs, and online services — perfect for IoT projects like this one.

### 🧩 Option 1 — Install via npm (recommended for Windows, macOS, Linux)

> 📦 Node-RED requires **Node.js ≥ 14** and **npm** installed first.  
> Download Node.js from [https://nodejs.org](https://nodejs.org).

1. Open **Terminal** (macOS/Linux) or **PowerShell** (Windows).
2. Install Node-RED globally:
   ```bash
   npm install -g --unsafe-perm node-red
