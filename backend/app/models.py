from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(32), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    role = Column(String(32), default="beekeeper") 
    cooperative = Column(String(256), nullable=True)
    wallet_address = Column(String(66), nullable=True)
    hashed_password = Column(String(256), nullable=True)
    device_id = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    batches = relationship("Batch", back_populates="beekeeper")
    hives = relationship("Hive", back_populates="beekeeper")

class Hive(Base):
    __tablename__ = "hives"

    id = Column(String(64), primary_key=True, index=True) # e.g. "HIVE-MZP-04"
    beekeeper_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    apiary_name = Column(String(256), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    state = Column(String(64), default="Bihar")
    district = Column(String(64), default="Muzaffarpur")
    floral_source = Column(String(128), default="Litchi Blossom")
    created_at = Column(DateTime, default=datetime.utcnow)

    beekeeper = relationship("User", back_populates="hives")
    batches = relationship("Batch", back_populates="hive")
    readings = relationship("SensorReading", back_populates="hive")

class Batch(Base):
    __tablename__ = "batches"

    id = Column(String(64), primary_key=True, index=True) # "BATCH-2026-KVIC-001"
    beekeeper_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    hive_id = Column(String(64), ForeignKey("hives.id"), nullable=True)
    
    harvest_date = Column(DateTime, default=datetime.utcnow)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    apiary_location = Column(String(256), nullable=True)
    floral_source = Column(String(128), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    farm_gate_price_per_kg = Column(Float, default=320.0)
    
    photos = Column(JSON, default=list)
    
    # Lab verification fields
    lab_purity_score = Column(Float, default=99.4)
    lab_moisture = Column(Float, default=17.4)
    lab_hmf = Column(Float, default=14.2)
    lab_c4_sugar = Column(String(64), default="0.0% (Non-Detected)")
    lab_status = Column(String(64), default="Verified Pure")
    lab_name = Column(String(256), default="KVIC Central Honey Testing Laboratory, Pune")
    lab_cert_number = Column(String(128), default="KVIC-CHTL-2026-8812")
    
    # On-Chain Anchoring
    batch_hash = Column(String(66), nullable=False)
    tx_hash = Column(String(66), nullable=True)
    anchored_by = Column(String(66), nullable=True)
    anchored_at = Column(DateTime, default=datetime.utcnow)
    
    # Fraud tracking
    device_id = Column(String(128), nullable=True)
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(String(256), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    beekeeper = relationship("User", back_populates="batches")
    hive = relationship("Hive", back_populates="batches")
    claims = relationship("ResaleClaim", back_populates="batch")

class ResaleClaim(Base):
    __tablename__ = "resale_claims"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(64), ForeignKey("batches.id"), nullable=False)
    claimant_address = Column(String(66), nullable=False)
    claimant_name = Column(String(128), default="Downstream Honey Brand")
    stage = Column(String(128), default="Retail Packaging & Distribution")
    quantity_sold = Column(Float, nullable=False)
    price_sold = Column(Float, nullable=False) # gross resale value
    unit_price = Column(Float, nullable=False) # per kg
    tx_hash = Column(String(66), nullable=True)
    claimed_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("Batch", back_populates="claims")

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    hive_id = Column(String(64), ForeignKey("hives.id"), nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    attestation_signature = Column(String(512), nullable=True)
    attestation_verified = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    hive = relationship("Hive", back_populates="readings")

class DeviceLog(Base):
    __tablename__ = "device_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    device_id = Column(String(128), nullable=False)
    action = Column(String(64), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    flagged_fraud = Column(Boolean, default=False)
    reason = Column(String(256), nullable=True)
