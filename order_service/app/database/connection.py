import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.order import Order, OrderItem, ShippingAddress

logger = logging.getLogger(__name__)

# Database connection
client: AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """Create database connection"""
    global client, database
    
    try:
        # Get connection details from environment
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        database_name = os.getenv("DATABASE_NAME", "ecommerce_orders")
        
        # Create client
        client = AsyncIOMotorClient(mongodb_url)
        database = client[database_name]
        
        # Test connection
        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB at {mongodb_url}")
        
        # Initialize Beanie with document models
        await init_beanie(
            database=database,
            document_models=[Order, OrderItem, ShippingAddress]
        )
        logger.info("Beanie initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection"""
    global client
    
    if client:
        try:
            client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")


async def get_database():
    """Get database instance"""
    return database


