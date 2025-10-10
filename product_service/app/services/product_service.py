from typing import Optional, List
from fastapi import HTTPException, status
from app.models.product import Product, Category
from app.repositories.product_repository import ProductRepository, CategoryRepository
from app.schemas.product_schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    ProductSearchQuery
)
import math


class CategoryService:
    """Service layer for Category business logic"""
    
    def __init__(self):
        self.category_repository = CategoryRepository()
    
    async def create_category(self, category_data: CategoryCreate) -> CategoryResponse:
        """Create a new category"""
        # Check if category with same name already exists
        existing_category = await self.category_repository.get_category_by_name(category_data.name)
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
        
        # Create category
        category_dict = category_data.dict()
        category = await self.category_repository.create_category(category_dict)
        
        return CategoryResponse(
            id=str(category.id),
            name=category.name,
            description=category.description,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
    
    async def get_category_by_id(self, category_id: str) -> CategoryResponse:
        """Get category by ID"""
        category = await self.category_repository.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return CategoryResponse(
            id=str(category.id),
            name=category.name,
            description=category.description,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
    
    async def get_all_categories(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[CategoryResponse]:
        """Get all categories"""
        categories = await self.category_repository.get_all_categories(skip, limit, active_only)
        return [
            CategoryResponse(
                id=str(category.id),
                name=category.name,
                description=category.description,
                is_active=category.is_active,
                created_at=category.created_at,
                updated_at=category.updated_at
            ) for category in categories
        ]
    
    async def update_category(self, category_id: str, update_data: CategoryUpdate) -> CategoryResponse:
        """Update category"""
        # Check if category exists
        existing_category = await self.category_repository.get_category_by_id(category_id)
        if not existing_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Check if name is being updated and if it conflicts
        if update_data.name and update_data.name != existing_category.name:
            name_conflict = await self.category_repository.get_category_by_name(update_data.name)
            if name_conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this name already exists"
                )
        
        # Update category
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        updated_category = await self.category_repository.update_category(category_id, update_dict)
        
        if not updated_category:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update category"
            )
        
        return CategoryResponse(
            id=str(updated_category.id),
            name=updated_category.name,
            description=updated_category.description,
            is_active=updated_category.is_active,
            created_at=updated_category.created_at,
            updated_at=updated_category.updated_at
        )
    
    async def delete_category(self, category_id: str) -> dict:
        """Delete category (soft delete)"""
        category = await self.category_repository.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        success = await self.category_repository.delete_category(category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete category"
            )
        
        return {"message": "Category deleted successfully"}


class ProductService:
    """Service layer for Product business logic"""
    
    def __init__(self):
        self.product_repository = ProductRepository()
        self.category_repository = CategoryRepository()
    
    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """Create a new product"""
        # Check if SKU already exists (if provided)
        if product_data.sku:
            existing_product = await self.product_repository.get_product_by_sku(product_data.sku)
            if existing_product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product with this SKU already exists"
                )
        
        # Validate and get category info if category_id is provided
        category_name = None
        if product_data.category_id:
            category = await self.category_repository.get_category_by_id(product_data.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found"
                )
            category_name = category.name
        
        # Create product
        product_dict = product_data.dict()
        product_dict["category_name"] = category_name
        product = await self.product_repository.create_product(product_dict)
        
        return ProductResponse(
            id=str(product.id),
            name=product.name,
            description=product.description,
            price=product.price,
            category_id=product.category_id,
            category_name=product.category_name,
            sku=product.sku,
            stock_quantity=product.stock_quantity,
            is_available=product.is_available,
            is_active=product.is_active,
            image_urls=product.image_urls,
            tags=product.tags,
            weight=product.weight,
            dimensions=product.dimensions,
            created_at=product.created_at,
            updated_at=product.updated_at
        )
    
    async def get_product_by_id(self, product_id: str) -> ProductResponse:
        """Get product by ID"""
        product = await self.product_repository.get_product_by_id(product_id)
        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return ProductResponse(
            id=str(product.id),
            name=product.name,
            description=product.description,
            price=product.price,
            category_id=product.category_id,
            category_name=product.category_name,
            sku=product.sku,
            stock_quantity=product.stock_quantity,
            is_available=product.is_available,
            is_active=product.is_active,
            image_urls=product.image_urls,
            tags=product.tags,
            weight=product.weight,
            dimensions=product.dimensions,
            created_at=product.created_at,
            updated_at=product.updated_at
        )
    
    async def get_all_products(self, skip: int = 0, limit: int = 20) -> ProductListResponse:
        """Get all products with pagination"""
        products = await self.product_repository.get_all_products(skip, limit)
        total = await self.product_repository.count_products()
        
        product_responses = [
            ProductResponse(
                id=str(product.id),
                name=product.name,
                description=product.description,
                price=product.price,
                category_id=product.category_id,
                category_name=product.category_name,
                sku=product.sku,
                stock_quantity=product.stock_quantity,
                is_available=product.is_available,
                is_active=product.is_active,
                image_urls=product.image_urls,
                tags=product.tags,
                weight=product.weight,
                dimensions=product.dimensions,
                created_at=product.created_at,
                updated_at=product.updated_at
            ) for product in products
        ]
        
        return ProductListResponse(
            products=product_responses,
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            total_pages=math.ceil(total / limit)
        )
    
    async def search_products(self, search_query: ProductSearchQuery) -> ProductListResponse:
        """Search products with filters"""
        skip = (search_query.page - 1) * search_query.per_page
        
        products = await self.product_repository.search_products(
            query=search_query.query,
            category_id=search_query.category_id,
            min_price=search_query.min_price,
            max_price=search_query.max_price,
            tags=search_query.tags,
            is_available=search_query.is_available,
            skip=skip,
            limit=search_query.per_page
        )
        
        # Count total matching products (simplified - would need proper count with filters)
        total = len(products)  # This is approximate, in production you'd want proper counting
        
        product_responses = [
            ProductResponse(
                id=str(product.id),
                name=product.name,
                description=product.description,
                price=product.price,
                category_id=product.category_id,
                category_name=product.category_name,
                sku=product.sku,
                stock_quantity=product.stock_quantity,
                is_available=product.is_available,
                is_active=product.is_active,
                image_urls=product.image_urls,
                tags=product.tags,
                weight=product.weight,
                dimensions=product.dimensions,
                created_at=product.created_at,
                updated_at=product.updated_at
            ) for product in products
        ]
        
        return ProductListResponse(
            products=product_responses,
            total=total,
            page=search_query.page,
            per_page=search_query.per_page,
            total_pages=math.ceil(total / search_query.per_page) if total > 0 else 1
        )
    
    async def update_product(self, product_id: str, update_data: ProductUpdate) -> ProductResponse:
        """Update product"""
        # Check if product exists
        existing_product = await self.product_repository.get_product_by_id(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Check SKU conflict if being updated
        if update_data.sku and update_data.sku != existing_product.sku:
            sku_conflict = await self.product_repository.get_product_by_sku(update_data.sku)
            if sku_conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product with this SKU already exists"
                )
        
        # Validate category if being updated
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        if update_data.category_id:
            category = await self.category_repository.get_category_by_id(update_data.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found"
                )
            update_dict["category_name"] = category.name
        
        # Update product
        updated_product = await self.product_repository.update_product(product_id, update_dict)
        
        if not updated_product:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update product"
            )
        
        return ProductResponse(
            id=str(updated_product.id),
            name=updated_product.name,
            description=updated_product.description,
            price=updated_product.price,
            category_id=updated_product.category_id,
            category_name=updated_product.category_name,
            sku=updated_product.sku,
            stock_quantity=updated_product.stock_quantity,
            is_available=updated_product.is_available,
            is_active=updated_product.is_active,
            image_urls=updated_product.image_urls,
            tags=updated_product.tags,
            weight=updated_product.weight,
            dimensions=updated_product.dimensions,
            created_at=updated_product.created_at,
            updated_at=updated_product.updated_at
        )
    
    async def delete_product(self, product_id: str) -> dict:
        """Delete product (soft delete)"""
        product = await self.product_repository.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        success = await self.product_repository.delete_product(product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete product"
            )
        
        return {"message": "Product deleted successfully"}
    
    async def update_stock(self, product_id: str, quantity_change: int) -> ProductResponse:
        """Update product stock"""
        product = await self.product_repository.update_stock(product_id, quantity_change)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product not found or insufficient stock"
            )
        
        return ProductResponse(
            id=str(product.id),
            name=product.name,
            description=product.description,
            price=product.price,
            category_id=product.category_id,
            category_name=product.category_name,
            sku=product.sku,
            stock_quantity=product.stock_quantity,
            is_available=product.is_available,
            is_active=product.is_active,
            image_urls=product.image_urls,
            tags=product.tags,
            weight=product.weight,
            dimensions=product.dimensions,
            created_at=product.created_at,
            updated_at=product.updated_at
        )

