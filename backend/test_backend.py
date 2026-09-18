"""
Standalone verification script for backend logic and cryptographic pipeline.
"""
import os
import sys
from datetime import datetime, timedelta

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.security import verify_tee_attestation, detect_device_fraud, create_access_token, decode_access_token
from app.blockchain import compute_canonical_batch_hash, blockchain_service
from app.ai_service import ai_service
from app.database import Base, engine, SessionLocal
from app.models import User, Hive, Batch, ResaleClaim, SensorReading

def run_tests():
    print("==================================================")
    print("HONEYCHAIN BACKEND COMPONENT VERIFICATION")
    print("==================================================")

    # 1. Test canonical hashing
    batch_data_1 = {"batchId": "TEST-01", "quantity": 50, "floral": "Litchi"}
    batch_data_2 = {"quantity": 50, "floral": "Litchi", "batchId": "TEST-01"}
    h1 = compute_canonical_batch_hash(batch_data_1)
    h2 = compute_canonical_batch_hash(batch_data_2)
    assert h1 == h2, "Canonical hashing must be key-order invariant!"
    print(f"[*] Canonical Keccak256 hash invariant: PASS ({h1})")

    # 2. Test TEE signature verification
    import hmac, hashlib
    from app.config import settings
    payload = b"HIVE-MZP-04:34.50:60.00:42.50"
    valid_sig = hmac.new(settings.TEE_ATTESTATION_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_tee_attestation(payload, valid_sig) == True
    assert verify_tee_attestation(payload, "invalid_sig_abc123") == False
    print("[*] TEE ARM TrustZone Attestation signature verification: PASS")

    # 3. Test fraud detection
    now = datetime.utcnow()
    # 500 km away in 30 minutes (impossible speed > 1000 km/h)
    is_fraud, msg = detect_device_fraud(26.12, 85.36, now - timedelta(minutes=30), 28.61, 77.20, now)
    assert is_fraud == True
    print(f"[*] Device speed fraud detection: PASS (Flagged: {msg})")

    # Normal rural move (5 km in 2 hours)
    is_fraud_normal, _ = detect_device_fraud(26.12, 85.36, now - timedelta(hours=2), 26.15, 85.38, now)
    assert is_fraud_normal == False
    print("[*] Normal relocation validation: PASS (Allowed)")

    # 4. Test AI Disease & Health scoring
    res_disease = ai_service.analyze_hive_frame_image(filename="varroa_infestation_01.jpg")
    assert res_disease["detected_condition"] == "Varroa Mite Infestation"
    print(f"[*] AI Disease detection inference: PASS ({res_disease['detected_condition']})")

    forecast = ai_service.predict_yield_forecast(current_weight_kg=42.5, daily_rate_kg=0.85, days=14)
    assert forecast["predicted_yield_kg"] > 0
    print(f"[*] AI 14-day Yield regression forecast: PASS ({forecast['predicted_yield_kg']} kg predicted)")

    # 5. Test Database creation and queries
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        print(f"[*] Database schema initialized successfully (Users count: {user_count})")
    finally:
        db.close()

    print("==================================================")
    print("ALL BACKEND INTERNAL TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
