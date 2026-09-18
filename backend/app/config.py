import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "HoneyChain API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = ""

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./honeychain.db")

    SECRET_KEY: str = os.getenv(
        "JWT_SECRET", "honeychain-sih2026-kvic-msme-blockchain-secret-key-998811")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    POLYGON_RPC_URL: str = os.getenv(
        "POLYGON_RPC_URL", "https://rpc-amoy.polygon.technology")
    CONTRACT_ADDRESS: str = os.getenv(
        "CONTRACT_ADDRESS", "0x3B997a0668b5aE387532B038fAfeF49f2b80016B")
    PRIVATE_KEY: str = os.getenv(
        "PRIVATE_KEY", "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")

    TEE_ATTESTATION_SECRET: str = os.getenv(
        "TEE_ATTESTATION_SECRET", "HONEYCHAIN_TEE_ARM_TRUSTZONE_ENCLAVE_KEY_2026")

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")

    ROYALTY_PERCENTAGE: float = 15.0

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"


settings = Settings()
