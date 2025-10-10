import os
import httpx
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class UserServiceClient:
    """Client for communicating with User Service"""
    
    def __init__(self):
        self.base_url = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
        self.timeout = 30.0
    
    async def get_user_by_id(self, user_id: str, token: str) -> Optional[Dict[str, Any]]:
        """Get user information by ID"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(
                    f"{self.base_url}/api/v1/users/profile/{user_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get user {user_id}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def verify_user_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify user token and get user info"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(
                    f"{self.base_url}/api/v1/users/profile",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to verify token: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None


class ProductServiceClient:
    """Client for communicating with Product Service"""
    
    def __init__(self):
        self.base_url = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8001")
        self.timeout = 30.0
    
    async def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product information by ID"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/products/{product_id}")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get product {product_id}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {e}")
            return None
    
    async def get_products_by_ids(self, product_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get multiple products by IDs"""
        products = {}
        
        for product_id in product_ids:
            product = await self.get_product_by_id(product_id)
            if product:
                products[product_id] = product
        
        return products
    
    async def check_product_availability(
        self, 
        product_id: str, 
        quantity: int
    ) -> Dict[str, Any]:
        """Check if product is available in requested quantity"""
        try:
            product = await self.get_product_by_id(product_id)
            
            if not product:
                return {
                    "available": False,
                    "reason": "Product not found",
                    "available_quantity": 0
                }
            
            if not product.get("is_available", False):
                return {
                    "available": False,
                    "reason": "Product not available",
                    "available_quantity": 0
                }
            
            stock_quantity = product.get("stock_quantity", 0)
            
            if stock_quantity < quantity:
                return {
                    "available": False,
                    "reason": "Insufficient stock",
                    "available_quantity": stock_quantity,
                    "requested_quantity": quantity
                }
            
            return {
                "available": True,
                "available_quantity": stock_quantity,
                "product": product
            }
            
        except Exception as e:
            logger.error(f"Error checking product availability {product_id}: {e}")
            return {
                "available": False,
                "reason": "Service error",
                "available_quantity": 0
            }
    
    async def reserve_products(
        self, 
        items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Reserve products for an order (mock implementation)"""
        # In a real implementation, this would call a product reservation endpoint
        # For now, we'll just validate availability
        
        reservations = []
        total_reserved = 0
        
        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]
            
            availability = await self.check_product_availability(product_id, quantity)
            
            if availability["available"]:
                reservations.append({
                    "product_id": product_id,
                    "quantity": quantity,
                    "reserved": True,
                    "product": availability["product"]
                })
                total_reserved += 1
            else:
                reservations.append({
                    "product_id": product_id,
                    "quantity": quantity,
                    "reserved": False,
                    "reason": availability["reason"],
                    "available_quantity": availability.get("available_quantity", 0)
                })
        
        return {
            "success": total_reserved == len(items),
            "total_items": len(items),
            "reserved_items": total_reserved,
            "reservations": reservations
        }
    
    async def update_product_stock(
        self, 
        product_id: str, 
        quantity_change: int
    ) -> bool:
        """Update product stock (mock implementation)"""
        # In a real implementation, this would call a stock update endpoint
        # For now, we'll just log the action
        
        try:
            logger.info(f"Stock update request for product {product_id}: {quantity_change}")
            
            # Mock API call
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.patch(
                    f"{self.base_url}/api/v1/products/{product_id}/stock",
                    json={"quantity_change": quantity_change}
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error updating product stock {product_id}: {e}")
            return False


# Global service clients
user_service_client = UserServiceClient()
product_service_client = ProductServiceClient()


