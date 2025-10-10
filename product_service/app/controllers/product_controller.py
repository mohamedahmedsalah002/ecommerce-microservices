from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from app.services.product_service import ProductService, CategoryService
from app.schemas.product_schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    ProductSearchQuery, StandardResponse
)


# Category router
category_router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


@category_router.post("/", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category_data: CategoryCreate):
    """
    Create a new category
    
    - **name**: Category name (2-100 characters, must be unique)
    - **description**: Optional category description (max 500 characters)
    """
    category_service = CategoryService()
    try:
        category = await category_service.create_category(category_data)
        return StandardResponse(
            success=True,
            message="Category created successfully",
            data=category.dict()
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@category_router.get("/", response_model=List[CategoryResponse])
async def get_all_categories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    active_only: bool = Query(default=True)
):
    """
    Get all categories with pagination
    
    - **skip**: Number of categories to skip (default: 0)
    - **limit**: Number of categories to return (default: 100, max: 100)
    - **active_only**: Return only active categories (default: true)
    """
    category_service = CategoryService()
    try:
        categories = await category_service.get_all_categories(skip, limit, active_only)
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@category_router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_by_id(category_id: str):
    """
    Get category by ID
    
    - **category_id**: Category ID
    """
    category_service = CategoryService()
    try:
        category = await category_service.get_category_by_id(category_id)
        return category
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@category_router.put("/{category_id}", response_model=StandardResponse)
async def update_category(category_id: str, update_data: CategoryUpdate):
    """
    Update category information
    
    - **category_id**: Category ID
    - **name**: New category name (optional)
    - **description**: New category description (optional)
    - **is_active**: Active status (optional)
    """
    category_service = CategoryService()
    try:
        updated_category = await category_service.update_category(category_id, update_data)
        return StandardResponse(
            success=True,
            message="Category updated successfully",
            data=updated_category.dict()
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@category_router.delete("/{category_id}", response_model=StandardResponse)
async def delete_category(category_id: str):
    """
    Delete category (soft delete)
    
    - **category_id**: Category ID
    """
    category_service = CategoryService()
    try:
        result = await category_service.delete_category(category_id)
        return StandardResponse(
            success=True,
            message=result["message"]
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Product router
product_router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@product_router.post("/", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate):
    """
    Create a new product
    
    - **name**: Product name (2-200 characters)
    - **description**: Product description (10-2000 characters)
    - **price**: Product price (must be > 0)
    - **category_id**: Category ID (optional)
    - **sku**: Stock Keeping Unit (optional, must be unique)
    - **stock_quantity**: Initial stock quantity (default: 0)
    - **is_available**: Availability status (default: true)
    - **image_urls**: List of image URLs (optional)
    - **tags**: List of product tags (optional)
    - **weight**: Product weight in kg (optional)
    - **dimensions**: Product dimensions dict (optional)
    """
    product_service = ProductService()
    try:
        product = await product_service.create_product(product_data)
        return StandardResponse(
            success=True,
            message="Product created successfully",
            data=product.dict()
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@product_router.get("/", response_model=ProductListResponse)
async def get_all_products(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100)
):
    """
    Get all products with pagination
    
    - **page**: Page number (default: 1)
    - **per_page**: Products per page (default: 20, max: 100)
    """
    product_service = ProductService()
    try:
        skip = (page - 1) * per_page
        products = await product_service.get_all_products(skip, per_page)
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@product_router.get("/search", response_model=ProductListResponse)
async def search_products(
    query: Optional[str] = Query(None, description="Search query for name/description/tags"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Products per page")
):
    """
    Search products with various filters
    
    - **query**: Text search in product name, description, and tags
    - **category_id**: Filter by specific category
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    - **tags**: Comma-separated list of tags to filter by
    - **is_available**: Filter by availability status
    - **page**: Page number for pagination
    - **per_page**: Number of products per page
    """
    product_service = ProductService()
    try:
        # Parse tags if provided
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
        
        search_query = ProductSearchQuery(
            query=query,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            tags=tag_list,
            is_available=is_available,
            page=page,
            per_page=per_page
        )
        
        products = await product_service.search_products(search_query)
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@product_router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(product_id: str):
    """
    Get product by ID
    
    - **product_id**: Product ID
    """
    product_service = ProductService()
    try:
        product = await product_service.get_product_by_id(product_id)
        return product
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@product_router.put("/{product_id}", response_model=StandardResponse)
async def update_product(product_id: str, update_data: ProductUpdate):
    """
    Update product information
    
    - **product_id**: Product ID
    - All product fields are optional for updates
    """
    product_service = ProductService()
    try:
        updated_product = await product_service.update_product(product_id, update_data)
        return StandardResponse(
            success=True,
            message="Product updated successfully",
            data=updated_product.dict()
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@product_router.delete("/{product_id}", response_model=StandardResponse)
async def delete_product(product_id: str):
    """
    Delete product (soft delete)
    
    - **product_id**: Product ID
    """
    product_service = ProductService()
    try:
        result = await product_service.delete_product(product_id)
        return StandardResponse(
            success=True,
            message=result["message"]
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@product_router.patch("/{product_id}/stock", response_model=StandardResponse)
async def update_product_stock(
    product_id: str,
    quantity_change: int = Query(..., description="Stock quantity change (positive or negative)")
):
    """
    Update product stock quantity
    
    - **product_id**: Product ID
    - **quantity_change**: Amount to add/subtract from current stock (can be negative)
    """
    product_service = ProductService()
    try:
        updated_product = await product_service.update_stock(product_id, quantity_change)
        return StandardResponse(
            success=True,
            message="Stock updated successfully",
            data=updated_product.dict()
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

