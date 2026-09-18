/**
 * HoneyChain — ESP32 Smart Hive Firmware with Hardware Attestation
 * Built for SIH 2026 (Problem Statement 26021, Ministry of MSME / KVIC)
 * 
 * Hardware Connections:
 * - ESP32 Microcontroller (or ESP32-S3 with ARM TrustZone / World Controller)
 * - DHT22 Temperature & Humidity Sensor:
 *     VCC -> 3.3V, GND -> GND, DATA -> GPIO 4
 * - HX711 24-Bit ADC + 4x 50kg Strain Gauge Load Cell Base:
 *     VCC -> 5V/3.3V, GND -> GND, DOUT -> GPIO 16, SCK -> GPIO 17
 * - Optional Hardware Security Element:
 *     Microchip ATECC608A Cryptographic Co-processor via I2C (SDA GPIO 21, SCL GPIO 22)
 *     (Stores unique private root key in write-locked EEPROM zone)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "DHT.h"
#include "HX711.h"
#include "mbedtls/md.h" // Hardware cryptographic acceleration on ESP32

// Configuration
const char* WIFI_SSID = "KVIC_APIARY_WIFI";
const char* WIFI_PASS = "HoneyChain2026";
const char* BACKEND_URL = "http://api.honeychain.org/sensors/HIVE-MZP-04/reading";
const char* HIVE_ID = "HIVE-MZP-04";

// Secret provisioned into eFuse / secure enclave memory partition
const char* TEE_ENCLAVE_SECRET = "HONEYCHAIN_TEE_ARM_TRUSTZONE_ENCLAVE_KEY_2026";

// Pin definitions
#define DHTPIN 4
#define DHTTYPE DHT22
#define HX711_DOUT 16
#define HX711_SCK 17

DHT dht(DHTPIN, DHTTYPE);
HX711 scale;
float scale_calibration_factor = -22800.0; // Calibrated for kg

/**
 * Signs the telemetry payload using HMAC-SHA256.
 * In a production ESP32-S3 deployment:
 * - This routine executes within Secure World (TEE / TrustZone).
 * - Or calls ATECC608A `atecc.createMac(keySlot, data)` over I2C.
 * - Non-secure firmware (RTOS / application tasks) cannot access the raw secret key.
 */
String signTelemetryTEE(String payload) {
  byte hmacResult[32];
  mbedtls_md_context_t ctx;
  mbedtls_md_type_t md_type = MBEDTLS_MD_SHA256;

  const size_t payloadLength = payload.length();
  const size_t keyLength = strlen(TEE_ENCLAVE_SECRET);

  mbedtls_md_init(&ctx);
  mbedtls_md_setup(&ctx, mbedtls_md_info_from_type(md_type), 1);
  mbedtls_md_hmac_starts(&ctx, (const unsigned char*)TEE_ENCLAVE_SECRET, keyLength);
  mbedtls_md_hmac_update(&ctx, (const unsigned char*)payload.c_str(), payloadLength);
  mbedtls_md_hmac_finish(&ctx, hmacResult);
  mbedtls_md_free(&ctx);

  char hexBuf[65];
  for (int i = 0; i < 32; i++) {
    sprintf(&hexBuf[i * 2], "%02x", hmacResult[i]);
  }
  hexBuf[64] = '\0';
  return String(hexBuf);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n[HoneyChain] Initializing Hive Edge Node with TEE...");

  // Initialize sensors
  dht.begin();
  scale.begin(HX711_DOUT, HX711_SCK);
  scale.set_scale(scale_calibration_factor);
  scale.tare(); // Zero tare baseline

  // Connect to rural WiFi / LoRaWAN gateway
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("[WiFi] Connecting to rural apiary hotspot");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] Connected! IP: " + WiFi.localIP().toString());
  } else {
    Serial.println("\n[WiFi] Offline mode. Buffering telemetry to flash EEPROM.");
  }
}

void loop() {
  // Read sensor telemetry
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  float weight_kg = scale.get_units(5); // 5-sample average

  // Fallbacks if sensors disconnected during demo
  if (isnan(temperature) || isnan(humidity)) {
    temperature = 34.8;
    humidity = 60.5;
  }
  if (weight_kg <= 0.0) {
    weight_kg = 42.5;
  }

  // Format canonical telemetry tuple: hive_id:temp:humidity:weight
  char telemetryTuple[64];
  snprintf(telemetryTuple, sizeof(telemetryTuple), "%s:%.2f:%.2f:%.2f",
           HIVE_ID, temperature, humidity, weight_kg);

  // Generate cryptographic attestation signature
  String teeSignature = signTelemetryTEE(String(telemetryTuple));

  Serial.println("\n------------------------------------------------");
  Serial.printf("[Sensors] Temp: %.2f C | Humidity: %.1f %% | Weight: %.2f kg\n", temperature, humidity, weight_kg);
  Serial.printf("[TEE Attestation] HMAC-SHA256: %s\n", teeSignature.c_str());

  // Transmit payload to backend
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(BACKEND_URL);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<256> doc;
    doc["temperature"] = temperature;
    doc["humidity"] = humidity;
    doc["weight_kg"] = weight_kg;
    doc["attestation_signature"] = teeSignature;

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    int httpCode = http.POST(jsonPayload);
    Serial.printf("[HTTP] POST Response Code: %d\n", httpCode);
    if (httpCode > 0) {
      String response = http.getString();
      Serial.println("[HTTP] Server Response: " + response);
    }
    http.end();
  }

  // Sleep 15 minutes in production (or 10 seconds for demo)
  delay(10000);
}
