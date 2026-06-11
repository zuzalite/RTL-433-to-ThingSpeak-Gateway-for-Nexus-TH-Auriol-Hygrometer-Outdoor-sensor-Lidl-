# RTL-433-to-ThingSpeak-Gateway-for-Nexus-TH-Auriol-Hygrometer-Outdoor-sensor-Lidl-


# RTL-433 to ThingSpeak Humidity Gateway

A lightweight Python utility script that pipes live radio frequency data from standard input (`sys.stdin`), parses telemetry packets targeting a specific weather sensor, and securely uploads humidity data to a **ThingSpeak** cloud channel. 

The script features a built-in software-level **anti-throttling timer** to respect ThingSpeak's 15-second rate limit for free accounts.

---

## 📐 System Architecture

This script acts as a middleware gateway in a pipeline. In a typical deployment, an SDR (Software Defined Radio) receiver demodulates 433.92 MHz weather sensor signals, outputs text logs, and pipes them directly into this script.

[433 MHz Sensor] ---> (SDR Dongle / rtl_433) ---> [This Python Script (sys.stdin)] ---> [ThingSpeak Cloud]


### Hardware Deployment Context
* **Host Receiver:** Usually runs on a Linux system (Raspberry Pi, home server, or PC) equipped with an RTL-SDR USB dongle.
* **Target Sensor:** 433 MHz ISM-band wireless sensor (specifically matching the **Nexus-TH** protocol with **House Code: 91**).

---

## 🧠 How the Software Logic Works

The script reads incoming terminal output line-by-line using a state-machine parser driven by regular expressions (`re` module):

### 1. Device Identification Block
Wireless receivers pick up every local sensor in range. To avoid uploading data from your neighbor's hardware, the parser monitors text blocks. It triggers data extraction **only** when a line matches both criteria:
* The string contains `model` and `Nexus-TH`.
* The string contains `House Code : 91` (validated via `re.search(r"House\s*Code\s*:\s*91")`).

### 2. Regex-Based Extraction
Once your target device block is active, the script looks for the `Humidity` descriptor. It extracts the raw integers using:
```regex
Humidity\s*:\s*([0-9]+)

The script performs sanity-check boundary filtering (0 <= value <= 100) before declaring the data valid to prevent corrupt payloads from skewing cloud charts.


Anti-Throttling Logic & CooldownThingSpeak's API rejects updates that occur faster than once every 15 seconds.
If multiple telemetry bursts arrive simultaneously, the script evaluates the delta time using time.time().
If $\Delta t \ge 16$ seconds: The JSON payload is posted to the endpoint https://api.thingspeak.com/update.json.
If $\Delta t < 16$ seconds: The entry is dropped quietly to prevent the cloud API from flagging or temporarily blocking the device token.


🚀 How to Run the Script
Prerequisites
Make sure your system has the Python requests library installed:    pip install requests

Manual Testing
You can manually test the script's matching state machine by typing or echoing mock data into it:
stdbuf -oL -eL rtl_433 | python3 -u /home/user name/Nexus_Final.py

