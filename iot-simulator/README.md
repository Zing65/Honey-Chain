# HoneyChain — IoT + TEE Simulator & Firmware (`/iot-simulator`)

## Overview

The IoT layer for **HoneyChain** (SIH 2026 Problem Statement 26021, Ministry of MSME / KVIC).

In smart apiculture, physical sensors monitor colony health and early disease indicators. However, raw IoT data is susceptible to spoofing (e.g. inflating weight to fake harvest volume). HoneyChain solves this with **Trusted Execution Environment (TEE) hardware attestation**.

---

## What the TEE Attestation Proves

- **Root of Trust**: Each sensor node holds a cryptographic key pair provisioned into hardware fuses (ARM TrustZone / ATECC608A secure element).
- **Tamper-Proof Ingestion**: Sensor readings `(hive_id, temp, humidity, weight)` are signed inside the secure enclave before network transmission.
- **Backend Verification**: The FastAPI backend checks the HMAC/ECDSA signature before accepting the reading into the colony health calculation engine.

---

## Running the Simulator

### Python Simulator
```bash
python simulate_hive.py --hive-id HIVE-MZP-04 --interval 2 --count 10
```

### Node.js Simulator
```bash
node simulate_hive.js
```

---

## ESP32 Physical Hardware Firmware

If an ESP32 microcontroller with DHT22 (temperature/humidity) and HX711 (load cell) is available, flash:
- [`HoneyChain_ESP32_TEE.ino`](HoneyChain_ESP32_TEE.ino)

The sketch utilizes ESP32 hardware `mbedtls` cryptographic acceleration to sign all measurements prior to HTTP/WiFi transmission.
