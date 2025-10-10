from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.models.product import Product, Category


class CategoryRepository:
    """Repository layer for Category data access operations"""
    
    @staticmethod
    async def create_category(category_data: dict) -> Category:
        """Create a new category in the database"""
        category = Category(**category_data)
        await category.insert()
        return category
    
    @staticmethod
    async def get_category_by_id(category_id: str) -> Optional[Category]:
        """Get category by ID"""
        try:
            return await Category.get(ObjectId(category_id))
        except Exception:
            return None
    
    @staticmethod
    async def get_category_by_name(name: str) -> Optional[Category]:
        """Get category by name"""
        return await Category.find_one(Category.name == name)
    
    @staticmethod
    async def get_all_categories(skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Category]:
        """Get all categories with pagination"""
        query = Category.find()
        if active_only:
            query = Category.find(Category.is_active == True)
        return await query.skip(skip).limit(limit).to_list()
    
    @staticmethod
    async def update_category(category_id: str, update_data: dict) -> Optional[Category]:
        """Update category information"""
        try:
            category = await Category.get(ObjectId(category_id))
            if category:
                for field, value in update_data.items():
                    if hasattr(category, field):
                        setattr(category, field, value)
                
                from datetime import datetime
                category.updated_at = datetime.utcnow()
                await category.save()
                return category
            return None
        except Exception:
            return None
    
    @staticmethod
    async def delete_category(category_id: str) -> bool:
        """Delete a category (soft delete by setting is_active to False)"""
        try:
            category = await Category.get(ObjectId(category_id))
            if category:
                category.is_active = False
                from datetime import datetime
                category.updated_at = datetime.utcnow()
                await category.save()
                return True
            return False
        except Exception:
            return False


class ProductRepository:
    """Repository layer for Product data access operations"""
    
    @staticmethod
    async def create_product(product_data: dict) -> Product:
        """Create a new product in the database"""
        product = Product(**product_data)
        await product.insert()
        return product
    
    @staticmethod
    async def get_product_by_id(product_id: str) -> Optional[Product]:
        """Get product by ID"""
        try:
            return await Product.get(ObjectId(product_id))
        except Exception:
            return None
    
    @staticmethod
    async def get_product_by_sku(sku: str) -> Optional[Product]:
        """Get product by SKU"""
        return await Product.find_one(Product.sku == sku)
    
    @staticmethod
    async def get_all_products(skip: int = 0, limit: int = 20, active_only: bool = True) -> List[Product]:
        """Get all products with pagination"""
        query = Product.find()
        if active_only:
            query = Product.find(Product.is_active == True)
        return await query.skip(skip).limit(limit).to_list()
    
    @staticmethod
    async def get_products_by_category(category_id: str, skip: int = 0, limit: int = 20) -> List[Product]:
        """Get products by category"""
        return await Product.find(
            Product.category_id == category_id, 
            Product.is_active == True
        ).skip(skip).limit(limit).to_list()
    
    @staticmethod
    async def search_products(
        query: Optional[str] = None,
        category_id: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        tags: Optional[List[str]] = None,
        is_available: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Product]:
        """Search products with various filters"""
        filters = [Product.is_active == True]
        
        if query:
            # Text search in name and description
            filters.append(
                {"$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                    {"tags": {"$in": [query]}}
                ]}
            )
        
        if category_id:
            filters.append(Product.category_id == category_id)
        
        if min_price is not None:
            filters.append(Product.price >= min_price)
        
        if max_price is not None:
            filters.append(Product.price <= max_price)
        
        if tags:
            filters.append(Product.tags.in_(tags))
        
        if is_available is not None:
            filters.append(Product.is_available == is_available)
        
        # Combine all filters
        if len(filters) == 1:
            search_query = Product.find(filters[0])
        else:
            search_query = Product.find({"$and": filters})
        
        return await search_query.skip(skip).limit(limit).to_list()
    
    @staticmethod
    async def count_products(filters: Optional[Dict[str, Any]] = None) -> int:
        """Count products with optional filters"""
        if filters:
            return await Product.find(filters).count()
        return await Product.find(Product.is_active == True).count()
    
    @staticmethod
    async def update_product(product_id: str, update_data: dict) -> Optional[Product]:
        """Update product information"""
        try:
            product = await Product.get(ObjectId(product_id))
            if product:
                for field, value in update_data.items():
                    if hasattr(product, field):
                        setattr(product, field, value)
                
                from datetime import datetime
                product.updated_at = datetime.utcnow()
                await product.save()
                return product
            return None
        except Exception:
            return None
    
    @staticmethod
    async def delete_product(product_id: str) -> bool:
        """Delete a product (soft delete by setting is_active to False)"""
        try:
            product = await Product.get(ObjectId(product_id))
            if product:
                product.is_active = False
                from datetime import datetime
                product.updated_at = datetime.utcnow()
                await product.save()
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    async def update_stock(product_id: str, quantity_change: int) -> Optional[Product]:
        """Update product stock quantity"""
        try:
            product = await Product.get(ObjectId(product_id))
            if product:
                new_quantity = product.stock_quantity + quantity_change
                if new_quantity < 0:
                    return None  # Insufficient stock
                
                product.stock_quantity = new_quantity
                product.is_available = new_quantity > 0
                
                from datetime import datetime
                product.updated_at = datetime.utcnow()
                await product.save()
                return product
            return None
        except Exception:
            return None

