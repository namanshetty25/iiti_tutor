from motor.motor_asyncio import AsyncIOMotorClient
from core.config import Config

class Database:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect_db(cls):
        cls.client = AsyncIOMotorClient(Config.MONGO_URI)
        cls.db = cls.client[Config.DATABASE_NAME]

    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()

db = Database
