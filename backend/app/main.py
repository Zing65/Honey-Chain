import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import User, Hive, Batch, ResaleClaim, SensorReading
from app.security import get_password_hash
from app.api import auth, batches, sensors, disease

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for HoneyChain - Blockchain Honey Traceability, Fair-Trade Royalty Enforcement, IoT & AI Apiculture Management (SIH 2026 PS 26021, Ministry of MSME / KVIC)."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(auth.router)
app.include_router(batches.router)
app.include_router(sensors.router)
app.include_router(disease.router)


@app.on_event("startup")
def seed_initial_demo_data():
    db = SessionLocal()
    try:
        beekeeper = db.query(User).filter(
            User.phone_number == "+91 98765 43210").first()
        if not beekeeper:
            beekeeper = User(
                phone_number="+91 98765 43210",
                name="Rameshwar Ray",
                role="beekeeper",
                cooperative="Muzaffarpur Honey Producers Sahakari Samiti",
                wallet_address="0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
                hashed_password=get_password_hash("123456"),
                device_id="ANDROID-DEMO-DEVICE-01"
            )
            db.add(beekeeper)
            db.commit()
            db.refresh(beekeeper)

        hive = db.query(Hive).filter(Hive.id == "HIVE-MZP-04").first()
        if not hive:
            hive = Hive(
                id="HIVE-MZP-04",
                beekeeper_id=beekeeper.id,
                apiary_name="Bochahan Orchard Apiary #4",
                latitude=26.1209,
                longitude=85.3647,
                state="Bihar",
                district="Muzaffarpur",
                floral_source="Litchi Blossom (Unifloral)"
            )
            db.add(hive)
            db.commit()

        batch = db.query(Batch).filter(
            Batch.id == "BATCH-2026-KVIC-001").first()
        if not batch:
            batch = Batch(
                id="BATCH-2026-KVIC-001",
                beekeeper_id=beekeeper.id,
                hive_id=hive.id,
                latitude=26.1209,
                longitude=85.3647,
                apiary_location="Bochahan Orchard Apiary #4, Muzaffarpur, Bihar",
                floral_source="Litchi Blossom (Unifloral)",
                quantity_kg=50.0,
                farm_gate_price_per_kg=320.0,
                photos=["/uploads/sample_harvest.jpg"],
                lab_purity_score=99.4,
                lab_moisture=17.4,
                lab_hmf=14.2,
                lab_c4_sugar="0.0% (Non-Detected)",
                lab_status="Verified Pure",
                lab_name="KVIC Central Honey Testing Laboratory, Pune",
                lab_cert_number="KVIC-CHTL-2026-8812",
                batch_hash="0xd4e56740f876aef8c010b86a40d5f56745a118d0906a34e69aec8c0db1cb8fa3",
                tx_hash="0x9f4a8b72c5e1d3f60a48b11c97ef3e54b17ad254e6015c928731adbf9073ba82",
                anchored_by=beekeeper.wallet_address,
                anchored_at=datetime.utcnow(),
                device_id="ANDROID-DEMO-DEVICE-01"
            )
            db.add(batch)
            db.commit()

            claim1 = ResaleClaim(
                batch_id=batch.id,
                claimant_address="0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199",
                claimant_name="KVIC State Processing Center",
                stage="Procurement & Primary Centrifuging",
                quantity_sold=50.0,
                price_sold=26000.0,
                unit_price=520.0,
                tx_hash="0x1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff"
            )
            claim2 = ResaleClaim(
                batch_id=batch.id,
                claimant_address="0x14dC79964da2C08b23698B3D3cc7Ca32193d9955",
                claimant_name="Himalayan Herbal Retail Organics Ltd.",
                stage="Retail Shelf Packaging & Brand Distribution",
                quantity_sold=50.0,
                price_sold=47500.0,
                unit_price=950.0,
                tx_hash="0xbbbbccccddddeeeeffff0000111122223333444455556666777788889999aaaa"
            )
            db.add_all([claim1, claim2])
            db.commit()

        reading = db.query(SensorReading).filter(
            SensorReading.hive_id == "HIVE-MZP-04").first()
        if not reading:
            initial_reading = SensorReading(
                hive_id="HIVE-MZP-04",
                temperature=34.8,
                humidity=60.2,
                weight_kg=42.6,
                attestation_signature="TEE_SIMULATED_ARM_TRUSTZONE_SIG_VALID",
                attestation_verified=True,
                timestamp=datetime.utcnow()
            )
            db.add(initial_reading)
            db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "project": "HoneyChain",
        "description": "Blockchain Honey Traceability and Fair-Trade Royalty Protocol",
        "sih_problem_statement": "26021 (Ministry of MSME / KVIC)",
        "status": "OPERATIONAL",
        "blockchain_network": "Polygon Amoy Testnet (Chain ID 80002)",
        "docs_url": "/docs",
        "version": settings.VERSION
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
