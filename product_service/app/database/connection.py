import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.product import Product, Category


class Database:
    """Database connection and configuration"""
    
    client: AsyncIOMotorClient = None
    database = None


# Database instance
db = Database()


async def connect_to_mongo():
    """Create database connection"""
    # Get MongoDB URL from environment variable
    MONGODB_URL = os.getenv(
        "MONGODB_URL",
        "mongodb://localhost:27017"
    )
    DATABASE_NAME = os.getenv("DATABASE_NAME", "ecommerce_products")
    
    # Create client
    db.client = AsyncIOMotorClient(MONGODB_URL)
    db.database = db.client[DATABASE_NAME]
    
    # Initialize Beanie with the Product and Category models
    await init_beanie(database=db.database, document_models=[Product, Category])
    
    print(f"Connected to MongoDB: {DATABASE_NAME}")


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")


def get_database():
    """Get database instance"""
    return db.database

