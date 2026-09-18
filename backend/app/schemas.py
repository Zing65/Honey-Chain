from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    name: str

class LoginRequest(BaseModel):
    phone_number: str
    password: Optional[str] = "123456"
    device_id: Optional[str] = "ANDROID-DEVICE-TEST-01"

# Batch Schemas
class BatchCreate(BaseModel):
    batch_id: Optional[str] = None # Auto-generated if not supplied
    beekeeper_id: Optional[int] = 1
    hive_id: str = "HIVE-MZP-04"
    latitude: float = 26.1209
    longitude: float = 85.3647
    apiary_location: Optional[str] = "Bochahan Apiary, Muzaffarpur, Bihar"
    floral_source: str = "Litchi Blossom (Unifloral)"
    quantity_kg: float = 50.0
    farm_gate_price_per_kg: float = 320.0
    photos: List[str] = Field(default_factory=list)
    lab_purity_score: Optional[float] = 99.4
    lab_moisture: Optional[float] = 17.4
    lab_hmf: Optional[float] = 14.2
    lab_c4_sugar: Optional[str] = "0.0% (Non-Detected)"
    lab_status: Optional[str] = "Verified Pure"
    device_id: Optional[str] = "MOBILE-APP-HARVEST-01"

class ClaimCreate(BaseModel):
    claimant_address: str = "0x14dC79964da2C08b23698B3D3cc7Ca32193d9955"
    claimant_name: str = "Himalayan Forest Organics Ltd."
    stage: str = "Retail Packaging & Brand Distribution"
    quantity_kg: float = 50.0
    price_sold: float = 47500.0 # total retail resale amount
    unit_price: Optional[float] = 950.0

class BatchResponse(BaseModel):
    batch_id: str
    status: str
    verdict_headline: str
    verdict_subline: str
    beekeeper: Dict[str, Any]
    harvest: Dict[str, Any]
    quality: Dict[str, Any]
    blockchain: Dict[str, Any]
    royalty: Dict[str, Any]

class RoyaltyResponse(BaseModel):
    batch_id: str
    batch_hash: str
    farm_gate_price_inr: float
    shelf_price_inr: float
    value_gap_inr: float
    royalty_percentage: float
    royalty_owed_inr: float
    cumulative_sales_inr: float
    total_quantity_sold_kg: float
    beekeeper_wallet: str
    claim_count: int
    claims: List[Dict[str, Any]]

# Sensor Reading Schemas
class SensorReadingCreate(BaseModel):
    temperature: float
    humidity: float
    weight_kg: float
    timestamp: Optional[datetime] = None
    attestation_signature: Optional[str] = None # TEE signature

class HealthScoreResponse(BaseModel):
    hive_id: str
    colony_health_score: int # 0 to 100
    health_status: str # "EXCELLENT", "NORMAL", "ATTENTION", "CRITICAL"
    nectar_flow_rate_kg_day: float
    temperature_stability_index: float
    humidity_status: str
    stress_signals: List[str]
    last_reading: Dict[str, Any]

class ProductivityForecastResponse(BaseModel):
    hive_id: str
    forecast_days: int
    predicted_yield_kg: float
    confidence_interval_low_kg: float
    confidence_interval_high_kg: float
    estimated_revenue_inr: float
    factors: Dict[str, Any]

# Disease Detection Schemas
class DiseaseAnalysisResponse(BaseModel):
    detected_condition: str # "Healthy Brood", "Varroa Mite Infestation", "American Foulbrood"
    confidence_score: float # 0.0 to 1.0
    severity: str # "NONE", "MEDIUM", "HIGH"
    plain_language_explanation: str
    recommended_action: str
    kvic_helpline: str
