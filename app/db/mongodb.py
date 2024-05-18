# backend/app/db/mongodb.py

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongodb = MongoDB()

async def connect_to_mongo():
    mongodb.client = AsyncIOMotorClient(settings.mongo_uri)
    mongodb.db = mongodb.client[settings.mongo_db_name]
    print(f"Connected to MongoDB database: {settings.mongo_db_name}")

async def close_mongo_connection():
    mongodb.client.close()
    print("Closed MongoDB connection")
