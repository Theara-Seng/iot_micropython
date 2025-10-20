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
3. Start Node-RED
   ```bash
   node-red
4. Once started, open your browser and go to:
   ```bash
   http://localhost:1880

## 🗄️ Installing InfluxDB (v1.x)

InfluxDB is a time-series database used to store sensor and IoT data efficiently.

> 💡 This project was tested with **InfluxDB v1.12.2** (InfluxQL syntax).  
> Official downloads: [https://portal.influxdata.com/downloads/](https://portal.influxdata.com/downloads/)

---

### 🧩  Windows Installation
1. Open **PowerShell as Administrator** and start the server:
```bash
wget https://download.influxdata.com/influxdb/releases/v1.12.2/influxdb-1.12.2-windows.zip -UseBasicParsing -OutFile influxdb-1.12.2-windows.zip
```
Then
```bash
Expand-Archive .\influxdb-1.12.2-windows.zip -DestinationPath 'C:\Program Files\InfluxData\influxdb\'
```
2. In a PowerShell window, open the Influx shell:
```powershell
cd "C:\Program Files\InfluxData\influxdb"
.\influx.exe
```
3. In a new PowerShell window, open the Influx shell:
```powershell
cd "C:\Program Files\InfluxData\influxdb"
.\influx.exe -host 127.0.0.1
```

## 📊 Installing Grafana

Grafana is a powerful visualization platform for time-series data such as InfluxDB metrics.

> 💡 This project uses **Grafana v10+** and **InfluxQL** as the query language.

Official downloads:  
🔗 [https://grafana.com/grafana/download](https://grafana.com/grafana/download)

---

### 🧩 Windows Installation

1. Download the Windows installer (`grafana-enterprise-<version>.windows-amd64.msi`)  
   👉 [Grafana Download for Windows](https://grafana.com/grafana/download?platform=windows)

2. Run the installer (accept defaults).  
   Grafana will be installed as a **Windows Service** and starts automatically.

3. Verify the service is running:
   - Press **Windows + R**, type `services.msc`, press **Enter**.
   - Locate **Grafana** (or **Grafana Enterprise**).
   - If not running → right-click → **Start**.

   Or, from **PowerShell (Admin)**:
   ```powershell
   net start grafana
4. Open Grafana in your browser:
   ```powershell
   http://localhost:3000
   ```
   
   Default login:
   
   Username: admin

   Password: admin
