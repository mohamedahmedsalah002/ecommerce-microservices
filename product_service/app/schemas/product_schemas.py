from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal


# Category Schemas
class CategoryCreate(BaseModel):
    """Schema for category creation"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CategoryUpdate(BaseModel):
    """Schema for category update"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    """Schema for category response"""
    id: str
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Product Schemas
class ProductCreate(BaseModel):
    """Schema for product creation"""
    name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    price: float = Field(..., gt=0)
    category_id: Optional[str] = None
    sku: Optional[str] = Field(None, max_length=50)
    stock_quantity: int = Field(default=0, ge=0)
    is_available: bool = Field(default=True)
    image_urls: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[dict] = None


class ProductUpdate(BaseModel):
    """Schema for product update"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    price: Optional[float] = Field(None, gt=0)
    category_id: Optional[str] = None
    sku: Optional[str] = Field(None, max_length=50)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None
    is_active: Optional[bool] = None
    image_urls: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[dict] = None


class ProductResponse(BaseModel):
    """Schema for product response"""
    id: str
    name: str
    description: str
    price: float
    category_id: Optional[str]
    category_name: Optional[str]
    sku: Optional[str]
    stock_quantity: int
    is_available: bool
    is_active: bool
    image_urls: List[str]
    tags: List[str]
    weight: Optional[float]
    dimensions: Optional[dict]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema for product list response with pagination"""
    products: List[ProductResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class ProductSearchQuery(BaseModel):
    """Schema for product search query"""
    query: Optional[str] = None
    category_id: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    is_available: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class StandardResponse(BaseModel):
    """Standard API response schema"""
    success: bool
    message: str
    data: Optional[dict] = None

