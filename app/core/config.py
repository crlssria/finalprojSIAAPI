# backend/app/core/config.py
import os

# Manually set environment variables for debugging
os.environ['API_KEY'] = 'goldapi-d6zpslwboaudd-io'
os.environ['MONGO_URI'] = 'mongodb+srv://carlossoria10:carlossoria40@cluster0.hb1ihvt.mongodb.net/test'
os.environ['MONGO_DB_NAME'] = 'finalproject'
os.environ['JWT_SECRET_KEY'] = 'b4f8e8b9c7d6e5f4a3b2c1d0e9f8d7c6'

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Precious Metals API"
    api_key: str
    mongo_uri: str
    mongo_db_name: str
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"  # Add this line if not present
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()

# Print the settings to debug
print("API_KEY:", settings.api_key)
print("MONGO_URI:", settings.mongo_uri)
print("MONGO_DB_NAME:", settings.mongo_db_name)
