from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import User, DeviceLog
from app.schemas import Token, LoginRequest
from app.security import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication & User Management"])

@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == req.phone_number).first()
    
    # Auto-seed mock user for frictionless SIH demo if not exists
    if not user:
        role = "admin" if "admin" in req.phone_number or "99999" in req.phone_number else "beekeeper"
        name = "KVIC Apiculture Officer" if role == "admin" else "Rameshwar Patel"
        user = User(
            phone_number=req.phone_number,
            name=name,
            role=role,
            cooperative="Muzaffarpur Honey Producers Sahakari Samiti",
            wallet_address="0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
            hashed_password=get_password_hash(req.password or "123456"),
            device_id=req.device_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Log device usage
    if req.device_id:
        log = DeviceLog(
            user_id=user.id,
            device_id=req.device_id,
            action="LOGIN",
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()

    token = create_access_token(data={"sub": str(user.id), "role": user.role, "phone": user.phone_number})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role,
        "name": user.name
    }

@router.get("/me")
def get_current_user_profile(user_id: int = 1, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {
            "id": 1,
            "name": "Rameshwar Patel",
            "phone_number": "+91 98765 43210",
            "role": "beekeeper",
            "cooperative": "Muzaffarpur Honey Producers Sahakari Samiti",
            "wallet_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
        }
    return {
        "id": user.id,
        "name": user.name,
        "phone_number": user.phone_number,
        "role": user.role,
        "cooperative": user.cooperative,
        "wallet_address": user.wallet_address
    }
