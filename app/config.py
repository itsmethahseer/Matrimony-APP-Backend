from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://matrimony_user:matrimony_password@localhost:5432/matrimony_db"
    SECRET_KEY: str = "supersecretkeymatrimonyapplication12345!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    PROJECT_NAME: str = "Matrimony API"
    
    # UPI Payments Config
    MERCHANT_UPI_ID: str = "matrimonyapp@upi"
    MERCHANT_NAME: str = "Matrimony Services"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
