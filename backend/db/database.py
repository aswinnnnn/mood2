from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os
import logging
from dotenv import load_dotenv
import certifi
from pathlib import Path

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

logger = logging.getLogger(__name__)

class Database:
    client = None
    db = None

    @classmethod
    async def connect_db(cls):
        if cls.client is not None:
            return  # Already connected
            
        try:
            # Get MongoDB URI from environment variable (check both names)
            mongodb_uri = os.getenv('MONGODB_URI') or os.getenv('MONGODB_URL')
            if not mongodb_uri:
                raise ValueError("MongoDB connection URI not set in environment variables")
            
            logger.info("Attempting to connect to MongoDB...")
            
            # Create client with server API version
            cls.client = AsyncIOMotorClient(
                mongodb_uri,
                server_api=ServerApi('1'),
                tlsCAFile=certifi.where()
            )
            
            # Get database name from URI or use default
            db_name = os.getenv('MONGODB_DB_NAME', 'moodscribe')
            cls.db = cls.client[db_name]
            
            # Verify connection
            await cls.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            cls.client = None
            cls.db = None
            raise

    @classmethod
    def get_db(cls):
        if cls.db is None:
            raise ConnectionError("Database not initialized. Call connect_db() first.")
        return cls.db

    @classmethod
    async def close_db(cls):
        if cls.client:
            await cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("MongoDB connection closed")

    @classmethod
    async def init_indexes(cls):
        try:
            db = cls.get_db()
            
            # Drop existing indexes first
            await db.users.drop_indexes()
            await db.user_preferences.drop_indexes()
            
            # Create new indexes with background=True for better performance
            await db.users.create_index(
                [("username", 1)], 
                unique=True,
                background=True,
                sparse=True  # Only index documents that have the username field
            )
            
            await db.users.create_index(
                [("email", 1)], 
                unique=True,
                background=True,
                sparse=True
            )
            
            await db.user_preferences.create_index(
                [("user_id", 1)], 
                unique=True,
                background=True
            )
            
            logger.info("Database indexes initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing indexes: {str(e)}")
            # Log the error but don't raise it - allow the application to continue
            pass 