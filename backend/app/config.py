from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List, Optional
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    APP_NAME: str = "Smart Dental Clinic Management System"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # Database
    # Default is SQLite for seamless local dev & testing, can be overridden with MySQL:
    # mysql+pymysql://dental_user:dental_pass@localhost:3306/dental_db
    DATABASE_URL: str = Field(default="sqlite:///./dental.db")
    DB_ECHO: bool = False
    
    # JWT Secrets
    JWT_SECRET_KEY: str = Field(default="dental-insecure-secret-key-change-in-prod-super-secure-token-98472918")
    JWT_REFRESH_SECRET_KEY: str = Field(default="dental-insecure-refresh-key-change-in-prod-ultra-secure-91823719")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Security & CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    
    # Storage
    STORAGE_TYPE: str = "local" # local or s3
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "jpg", "jpeg", "png", "webp", "dcm"]
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/webp",
        "application/dicom",
        "application/octet-stream"
    ]
    
    # Clinic Details for PDFs
    CLINIC_NAME: str = "Apex Dental Care & Implant Center"
    CLINIC_ADDRESS: str = "Suite 400, Healthcare Boulevard, Metro City"
    CLINIC_PHONE: str = "+1 (555) 321-4567"
    CLINIC_EMAIL: str = "contact@apexdental.com"
    CLINIC_WEBSITE: str = "www.apexdental.com"
    CLINIC_REG_NO: str = "REG-DENT-2024-8849"
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
