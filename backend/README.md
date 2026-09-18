# HoneyChain — FastAPI Backend (`/backend`)

## Overview

The core backend for **HoneyChain** (SIH 2026 Problem Statement 26021, Ministry of MSME / KVIC), orchestrating:
1. **Batch & QR Verification Service**: Anchors harvest batches, computes canonical Keccak256 hashes, interacts with `HoneyBatchRegistry.sol`, and handles downstream resale claims.
2. **IoT & Colony Health Analytics**: Ingests sensor readings with simulated ARM TrustZone TEE attestation signatures, computes colony health scores (weight trends, thermal stress), and forecasts yield.
3. **AI Disease Detection Service**: Runs image diagnosis on brood frames for Varroa Mite and Foulbrood diseases with immediate advisory.
4. **Auth & Anti-Fraud Service**: JWT authentication and device speed-anomaly fraud detection (flags impossible relocation between harvests).

---

## Local Development (Zero-Friction Setup)

The backend is configured to use SQLite by default (`sqlite:///./honeychain.db`), requiring zero database installation for instant local demonstration.

### Option 1: Direct Python Run
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Option 2: Docker Compose (FastAPI + PostgreSQL)
```bash
cd backend
docker-compose up --build
```

Interactive API documentation will be live at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/batches` | Submits harvest batch, validates fraud velocity, hashes canonically, anchors on Polygon Amoy. |
| `GET` | `/batches/{batch_id}` | Returns complete batch provenance and on-chain verification proof for QR scanner. |
| `POST` | `/batches/{batch_id}/claim` | Downstream brand records resale claim with markup price and triggers `claimBatch`. |
| `GET` | `/batches/{batch_id}/royalty` | Calculates cumulative 15% royalty owed back to the rural beekeeper. |
| `POST` | `/sensors/{hive_id}/reading` | Ingests IoT sensor telemetry after validating TEE attestation signature. |
| `GET` | `/hives/{hive_id}/health-score` | Computes colony health index (0–100) based on thermoregulation and nectar flow. |
| `GET` | `/hives/{hive_id}/productivity-forecast` | Regression forecast for 14-day honey yield. |
| `POST` | `/disease-detection/analyze` | AI image classification for Varroa mites and Foulbrood. |
| `POST` | `/auth/login` | Beekeeper / Admin JWT authentication with device ID tracking. |
