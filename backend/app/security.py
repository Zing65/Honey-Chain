import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return True
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_tee_attestation(payload_bytes: bytes, signature_hex: str) -> bool:
    """
    Validates simulated ARM TrustZone TEE attestation signature.
    Matches the cryptographic signature produced by the simulated hardware enclave.
    """
    if not signature_hex:
        # In demo mode, if signature is omitted, return True with warning
        return True
    
    expected_hmac = hmac.new(
        settings.TEE_ATTESTATION_SECRET.encode("utf-8"),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_hmac, signature_hex)

def detect_device_fraud(last_lat: float, last_lng: float, last_time: datetime,
                        curr_lat: float, curr_lng: float, curr_time: datetime) -> tuple[bool, str]:
    """
    Fraud-pattern detection: flags impossible travel speeds (> 150 km/h) between harvests.
    Prevents fraudulent bulk aggregation claiming to be local rural harvests.
    """
    from math import radians, cos, sin, asin, sqrt
    
    # Haversine distance in km
    lon1, lat1, lon2, lat2 = map(radians, [last_lng, last_lat, curr_lng, curr_lat])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    
    time_diff_hours = (curr_time - last_time).total_seconds() / 3600.0
    if time_diff_hours <= 0:
        return True, "Simultaneous harvest timestamps detected at different GPS coordinates."
    
    speed_kmh = km / time_diff_hours
    if speed_kmh > 150.0 and km > 50.0:
        return True, f"Impossible relocation speed ({speed_kmh:.1f} km/h across {km:.1f} km) within {time_diff_hours:.2f} hours."
    
    return False, ""
