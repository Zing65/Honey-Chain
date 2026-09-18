#!/usr/bin/env python3
"""
HoneyChain IoT + TEE Simulator (SIH 2026 Problem Statement 26021)
Simulates an ESP32 edge microcontroller equipped with:
- DHT22 (Ambient Brood Nest Temperature & Relative Humidity)
- HX711 (24-bit ADC + 4-Point Load Cell Colony Weight Scale)
- ARM TrustZone / ATECC608A Secure Enclave Attestation Signing
"""

import time
import json
import hmac
import hashlib
import random
import argparse
from datetime import datetime
import urllib.request
import urllib.error

# Simulated Secure Enclave Context (Representing ARM TrustZone hardware root-of-trust)
class ARMTrustZoneSecureEnclave:
    """
    Simulates the isolated execution environment (TEE).
    In physical hardware, this key is provisioned into hardware fuses (e.g. eFuse on ESP32-S3
    or ATECC608A secure element) and cannot be extracted by compromised firmware.
    """
    def __init__(self, enclave_secret="HONEYCHAIN_TEE_ARM_TRUSTZONE_ENCLAVE_KEY_2026"):
        self._enclave_private_secret = enclave_secret.encode("utf-8")

    def sign_sensor_telemetry(self, hive_id: str, temperature: float, humidity: float, weight_kg: float) -> str:
        """
        Signs the raw sensor measurement tuple inside the secure enclave boundary.
        Produces a tamper-proof cryptographic attestation signature.
        """
        telemetry_string = f"{hive_id}:{temperature:.2f}:{humidity:.2f}:{weight_kg:.2f}"
        signature = hmac.new(
            self._enclave_private_secret,
            telemetry_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature

class HiveSimulator:
    def __init__(self, hive_id="HIVE-MZP-04", backend_url="http://localhost:8000"):
        self.hive_id = hive_id
        self.backend_url = backend_url.rstrip("/")
        self.enclave = ARMTrustZoneSecureEnclave()
        
        # Initial colony baseline physics
        self.base_temperature = 34.8  # Optimal brood nest thermoregulation (~34.5 - 35.5 C)
        self.base_humidity = 60.5     # Optimal brood nest humidity (~55 - 65%)
        self.current_weight = 42.50   # Current gross hive weight in kg
        self.step = 0

    def generate_reading(self):
        """
        Simulates realistic diurnal and seasonal environmental factors.
        """
        self.step += 1
        
        # Diurnal fluctuation (bees maintain tight brood temp, but slight day/night variation)
        temp_noise = random.gauss(0, 0.25)
        temperature = round(self.base_temperature + temp_noise, 2)

        # Humidity fluctuates inversely with heat
        hum_noise = random.gauss(0, 0.8)
        humidity = round(max(40.0, min(80.0, self.base_humidity + hum_noise)), 1)

        # Weight gain simulation: foragers bringing in nectar during active foraging
        # Yield accumulates 0.02 - 0.08 kg per reading during active flow
        daily_nectar_gain = random.uniform(0.015, 0.055)
        self.current_weight = round(self.current_weight + daily_nectar_gain, 2)

        # Sign measurement inside the simulated ARM TrustZone enclave
        signature = self.enclave.sign_sensor_telemetry(
            self.hive_id, temperature, humidity, self.current_weight
        )

        return {
            "hive_id": self.hive_id,
            "temperature": temperature,
            "humidity": humidity,
            "weight_kg": self.current_weight,
            "timestamp": datetime.utcnow().isoformat(),
            "attestation_signature": signature
        }

    def transmit_reading(self, payload):
        endpoint = f"{self.backend_url}/sensors/{self.hive_id}/reading"
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return True, result
        except urllib.error.URLError as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)

    def run(self, interval_sec=2, count=None, verbose=True):
        print("\n========================================================")
        print(" HONEYCHAIN IoT + TEE SENSOR NODE SIMULATION")
        print(f" Hive Node ID:     {self.hive_id}")
        print(f" Backend Endpoint: {self.backend_url}/sensors/{self.hive_id}/reading")
        print(f" Hardware Enclave: ARM TrustZone / ATECC608A Active")
        print("========================================================\n")

        transmitted = 0
        try:
            while count is None or transmitted < count:
                reading = self.generate_reading()
                success, response = self.transmit_reading(reading)

                transmitted += 1
                status_str = "[OK 200]" if success else "[OFFLINE MOCK]"

                if verbose:
                    print(f"[{transmitted}] {reading['timestamp'][11:19]} {status_str} "
                          f"Temp: {reading['temperature']}°C | "
                          f"Humidity: {reading['humidity']}% | "
                          f"Weight: {reading['weight_kg']} kg | "
                          f"TEE Sig: {reading['attestation_signature'][:14]}...")

                if count is None or transmitted < count:
                    time.sleep(interval_sec)

        except KeyboardInterrupt:
            print("\n[!] Simulation paused by user.")
        
        print(f"\nCompleted {transmitted} sensor telemetry transmissions.")

def main():
    parser = argparse.ArgumentParser(description="HoneyChain IoT + TEE Telemetry Simulator")
    parser.add_argument("--hive-id", default="HIVE-MZP-04", help="Unique identifier of the hive")
    parser.add_argument("--backend-url", default="http://localhost:8000", help="FastAPI backend host")
    parser.add_argument("--interval", type=float, default=2.0, help="Interval between readings in seconds (default: 2s)")
    parser.add_argument("--count", type=int, default=10, help="Number of readings to send (default: 10, 0 for infinite)")
    args = parser.parse_args()

    count = None if args.count <= 0 else args.count
    sim = HiveSimulator(hive_id=args.hive_id, backend_url=args.backend_url)
    sim.run(interval_sec=args.interval, count=count)

if __name__ == "__main__":
    main()
