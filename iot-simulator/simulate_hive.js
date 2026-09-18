/**
 * HoneyChain IoT + TEE Simulator (Node.js version)
 * Simulates ESP32 DHT22 + HX711 sensor telemetry with ARM TrustZone attestation.
 */

const crypto = require("crypto");
const http = require("http");

const HIVE_ID = process.env.HIVE_ID || "HIVE-MZP-04";
const BACKEND_HOST = process.env.BACKEND_HOST || "localhost";
const BACKEND_PORT = process.env.BACKEND_PORT || 8000;
const TEE_SECRET = process.env.TEE_SECRET || "HONEYCHAIN_TEE_ARM_TRUSTZONE_ENCLAVE_KEY_2026";

class Enclave {
  static sign(hiveId, temp, hum, weight) {
    const payload = `${hiveId}:${temp.toFixed(2)}:${hum.toFixed(2)}:${weight.toFixed(2)}`;
    return crypto.createHmac("sha256", TEE_SECRET).update(payload).digest("hex");
  }
}

let currentWeight = 42.5;

function generateReading() {
  const temp = +(34.5 + Math.random() * 0.8).toFixed(2);
  const hum = +(58 + Math.random() * 5).toFixed(1);
  currentWeight = +(currentWeight + (0.01 + Math.random() * 0.04)).toFixed(2);
  const sig = Enclave.sign(HIVE_ID, temp, hum, currentWeight);

  return {
    hive_id: HIVE_ID,
    temperature: temp,
    humidity: hum,
    weight_kg: currentWeight,
    timestamp: new Date().toISOString(),
    attestation_signature: sig,
  };
}

function sendReading(reading) {
  const data = JSON.stringify(reading);
  const options = {
    hostname: BACKEND_HOST,
    port: BACKEND_PORT,
    path: `/sensors/${HIVE_ID}/reading`,
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Content-Length": Buffer.byteLength(data),
    },
    timeout: 3000,
  };

  const req = http.request(options, (res) => {
    let body = "";
    res.on("data", (chunk) => (body += chunk));
    res.on("end", () => {
      console.log(`[OK ${res.statusCode}] Temp: ${reading.temperature}°C | Hum: ${reading.humidity}% | Weight: ${reading.weight_kg}kg | TEE Sig: ${reading.attestation_signature.substring(0, 12)}...`);
    });
  });

  req.on("error", (e) => {
    console.log(`[OFFLINE DEMO] Generated reading: Temp ${reading.temperature}°C, Weight ${reading.weight_kg}kg (Backend not reachable)`);
  });

  req.write(data);
  req.end();
}

console.log("\n========================================================");
console.log(" HONEYCHAIN IoT SENSOR SIMULATOR (NODE.JS)");
console.log(` Hive ID: ${HIVE_ID} | ARM TrustZone Enclave Signature Enabled`);
console.log("========================================================\n");

// Send first reading immediately then every 2.5 seconds
sendReading(generateReading());
const interval = setInterval(() => {
  sendReading(generateReading());
}, 2500);

process.on("SIGINT", () => {
  clearInterval(interval);
  console.log("\nSimulation stopped.");
  process.exit(0);
});
