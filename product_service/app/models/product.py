from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from beanie import Document
from pydantic import BaseModel, Field
from bson import ObjectId


class Category(Document):
    """Category model using Beanie ODM for MongoDB"""
    
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "categories"  # MongoDB collection name
    
    class Config:
        json_encoders = {
            ObjectId: str
        }


class Product(Document):
    """Product model using Beanie ODM for MongoDB"""
    
    name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    price: float = Field(..., gt=0)  # Price must be greater than 0
    category_id: Optional[str] = Field(None)
    category_name: Optional[str] = Field(None)  # Denormalized for faster queries
    sku: Optional[str] = Field(None, max_length=50)  # Stock Keeping Unit
    stock_quantity: int = Field(default=0, ge=0)  # Must be >= 0
    is_available: bool = Field(default=True)
    is_active: bool = Field(default=True)
    image_urls: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    weight: Optional[float] = Field(None, gt=0)  # Weight in kg
    dimensions: Optional[dict] = Field(None)  # {"length": 10, "width": 5, "height": 3}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "products"  # MongoDB collection name
    
    class Config:
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "name": "iPhone 15 Pro",
                "description": "Latest iPhone with advanced camera system and A17 Pro chip",
                "price": 999.99,
                "category_name": "Electronics",
                "sku": "IPH15PRO128",
                "stock_quantity": 50,
                "is_available": True,
                "image_urls": ["https://example.com/iphone15pro.jpg"],
                "tags": ["smartphone", "apple", "electronics"],
                "weight": 0.221,
                "dimensions": {"length": 14.67, "width": 7.09, "height": 0.83}
            }
        }

