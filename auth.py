import os
from dotenv import load_dotenv
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

load_dotenv()  # Load environment variables from .env file

api_key_header = APIKeyHeader(name="X-API-Key")
API_KEY = os.getenv("API_KEY", "default-key-jika-tidak-ada")

def verifikasi_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="API Key tidak valid"
            )
    return key