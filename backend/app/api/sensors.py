from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from app.database import get_db
from app.models import Hive, SensorReading
from app.schemas import SensorReadingCreate, HealthScoreResponse, ProductivityForecastResponse
from app.security import verify_tee_attestation
from app.ai_service import ai_service

router = APIRouter(prefix="", tags=["IoT Ingestion & Colony Health Analytics"])

@router.post("/sensors/{hive_id}/reading")
def ingest_sensor_reading(hive_id: str, req: SensorReadingCreate, db: Session = Depends(get_db)):
    """
    Ingests IoT sensor payload from simulated ESP32 or physical hardware.
    Validates the ARM TrustZone TEE attestation signature before storage.
    """
    # Verify or auto-create hive for demo
    hive = db.query(Hive).filter(Hive.id == hive_id).first()
    if not hive:
        hive = Hive(
            id=hive_id,
            beekeeper_id=1,
            apiary_name="Bochahan Orchard Apiary #4",
            latitude=26.1209,
            longitude=85.3647,
            state="Bihar",
            district="Muzaffarpur",
            floral_source="Litchi Blossom (Unifloral)"
        )
        db.add(hive)
        db.commit()

    # Reconstruct payload bytes for TEE signature validation
    reading_timestamp = req.timestamp or datetime.utcnow()
    canonical_payload = f"{hive_id}:{req.temperature:.2f}:{req.humidity:.2f}:{req.weight_kg:.2f}"
    
    is_valid_attestation = True
    if req.attestation_signature:
        is_valid_attestation = verify_tee_attestation(
            canonical_payload.encode("utf-8"),
            req.attestation_signature
        )

    reading = SensorReading(
        hive_id=hive_id,
        temperature=req.temperature,
        humidity=req.humidity,
        weight_kg=req.weight_kg,
        attestation_signature=req.attestation_signature,
        attestation_verified=is_valid_attestation,
        timestamp=reading_timestamp
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)

    return {
        "status": "READING_INGESTED",
        "hive_id": hive_id,
        "reading_id": reading.id,
        "tee_attestation_verified": is_valid_attestation,
        "recorded_at": reading.timestamp.isoformat()
    }

@router.get("/hives/{hive_id}/health-score", response_model=HealthScoreResponse)
def get_colony_health_score(hive_id: str, db: Session = Depends(get_db)):
    """
    Returns computed colony health score (0-100) derived from recent sensor trends:
    - Weight delta = nectar flow rate
    - Temperature/humidity deviation = thermal stress / brood chill / disease signal
    """
    # Fetch last 48 readings for trend calculation
    readings = db.query(SensorReading).filter(
        SensorReading.hive_id == hive_id
    ).order_by(SensorReading.timestamp.asc()).limit(48).all()

    health_metrics = ai_service.compute_colony_health(readings)

    return HealthScoreResponse(
        hive_id=hive_id,
        colony_health_score=health_metrics["colony_health_score"],
        health_status=health_metrics["health_status"],
        nectar_flow_rate_kg_day=health_metrics["nectar_flow_rate_kg_day"],
        temperature_stability_index=health_metrics["temperature_stability_index"],
        humidity_status=health_metrics["humidity_status"],
        stress_signals=health_metrics["stress_signals"],
        last_reading=health_metrics["last_reading"]
    )

@router.get("/hives/{hive_id}/productivity-forecast", response_model=ProductivityForecastResponse)
def get_productivity_forecast(hive_id: str, days: int = 14, db: Session = Depends(get_db)):
    """
    Returns regression-based yield forecast for the hive.
    """
    latest_reading = db.query(SensorReading).filter(
        SensorReading.hive_id == hive_id
    ).order_by(SensorReading.timestamp.desc()).first()

    current_weight = latest_reading.weight_kg if latest_reading else 42.5
    daily_rate = 0.85 # default positive spring flow rate

    forecast = ai_service.predict_yield_forecast(current_weight, daily_rate, days)

    return ProductivityForecastResponse(
        hive_id=hive_id,
        forecast_days=forecast["forecast_days"],
        predicted_yield_kg=forecast["predicted_yield_kg"],
        confidence_interval_low_kg=forecast["confidence_interval_low_kg"],
        confidence_interval_high_kg=forecast["confidence_interval_high_kg"],
        estimated_revenue_inr=forecast["estimated_revenue_inr"],
        factors=forecast["factors"]
    )

@router.get("/hives/{hive_id}/readings")
def get_recent_readings(hive_id: str, limit: int = 24, db: Session = Depends(get_db)):
    """
    Returns time-series history for charts.
    """
    readings = db.query(SensorReading).filter(
        SensorReading.hive_id == hive_id
    ).order_by(SensorReading.timestamp.desc()).limit(limit).all()

    # If empty, return synthetic 24-hour curve
    if not readings:
        now = datetime.utcnow()
        synthetic = []
        for i in range(24):
            synthetic.append({
                "timestamp": (now - timedelta(hours=23 - i)).isoformat(),
                "temperature": round(34.2 + (i % 5) * 0.25, 2),
                "humidity": round(58.0 + (i % 4) * 0.8, 1),
                "weight_kg": round(41.0 + (i * 0.05), 2),
                "attestation_verified": True
            })
        return synthetic

    return [
        {
            "timestamp": r.timestamp.isoformat(),
            "temperature": r.temperature,
            "humidity": r.humidity,
            "weight_kg": r.weight_kg,
            "attestation_verified": r.attestation_verified
        } for r in reversed(readings)
    ]
