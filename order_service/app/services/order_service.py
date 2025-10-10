import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status

from app.models.order import Order, OrderItem, ShippingAddress, OrderStatus, PaymentStatus
from app.repositories.order_repository import OrderRepository
from app.schemas.order_schemas import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse, 
    OrderStats, OrderStatusUpdate, PaymentUpdate
)
from app.utils.external_services import user_service_client, product_service_client
from app.utils.kafka_producer import (
    publish_order_created_event, publish_order_confirmed_event,
    publish_order_cancelled_event, publish_order_shipped_event,
    publish_order_delivered_event, publish_payment_completed_event,
    publish_payment_failed_event
)

logger = logging.getLogger(__name__)

class OrderService:
    """Service layer for Order business logic"""
    
    def __init__(self):
        self.order_repository = OrderRepository()
    
    def _generate_order_number(self) -> str:
        """Generate unique order number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"ORD-{timestamp}-{random_suffix}"
    
    async def create_order(self, order_data: OrderCreate, user_token: str) -> OrderResponse:
        """Create a new order"""
        try:
            # Verify user token and get user info
            user_info = await user_service_client.verify_user_token(user_token)
            if not user_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
            
            user_id = user_info["id"]
            user_email = user_info["email"]
            
            # Validate and reserve products
            product_ids = [item.product_id for item in order_data.items]
            reservation_result = await product_service_client.reserve_products([
                {"product_id": item.product_id, "quantity": item.quantity}
                for item in order_data.items
            ])
            
            if not reservation_result["success"]:
                failed_items = [
                    res for res in reservation_result["reservations"] 
                    if not res["reserved"]
                ]
                error_details = []
                for item in failed_items:
                    error_details.append(
                        f"Product {item['product_id']}: {item.get('reason', 'Unknown error')}"
                    )
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product reservation failed: {'; '.join(error_details)}"
                )
            
            # Create order items with product information
            order_items = []
            subtotal = 0.0
            
            for item_data, reservation in zip(order_data.items, reservation_result["reservations"]):
                if reservation["reserved"]:
                    product = reservation["product"]
                    
                    # Create order item
                    order_item = OrderItem(
                        product_id=item_data.product_id,
                        product_name=product["name"],
                        product_sku=product.get("sku"),
                        unit_price=product["price"],
                        quantity=item_data.quantity,
                        total_price=product["price"] * item_data.quantity,
                        product_snapshot={
                            "name": product["name"],
                            "description": product.get("description", ""),
                            "price": product["price"],
                            "category_name": product.get("category_name"),
                            "image_urls": product.get("image_urls", [])
                        }
                    )
                    
                    order_items.append(order_item)
                    subtotal += order_item.total_price
            
            # Create shipping address
            shipping_address = ShippingAddress(**order_data.shipping_address.dict())
            await shipping_address.insert()
            
            # Calculate totals (simplified tax and shipping calculation)
            tax_rate = 0.08  # 8% tax rate
            tax_amount = round(subtotal * tax_rate, 2)
            shipping_cost = 10.0 if subtotal < 100 else 0.0  # Free shipping over $100
            total_amount = subtotal + tax_amount + shipping_cost
            
            # Create order
            order_dict = {
                "order_number": self._generate_order_number(),
                "user_id": user_id,
                "user_email": user_email,
                "items": order_items,
                "subtotal": subtotal,
                "tax_amount": tax_amount,
                "shipping_cost": shipping_cost,
                "discount_amount": 0.0,
                "total_amount": total_amount,
                "status": OrderStatus.PENDING,
                "payment_status": PaymentStatus.PENDING,
                "shipping_address": shipping_address,
                "shipping_method": order_data.shipping_method,
                "payment_method": order_data.payment_method,
                "notes": order_data.notes,
                "metadata": {}
            }
            
            order = await self.order_repository.create_order(order_dict)
            
            # Publish order created event
            order_event_data = {
                "id": str(order.id),
                "order_number": order.order_number,
                "user_id": order.user_id,
                "user_email": order.user_email,
                "total_amount": order.total_amount,
                "item_count": order.get_item_count(),
                "items": [
                    {
                        "product_id": item.product_id,
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price
                    }
                    for item in order.items
                ],
                "created_at": order.created_at.isoformat()
            }
            await publish_order_created_event(order_event_data)
            
            return await self._convert_to_response(order)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create order"
            )
    
    async def get_order_by_id(self, order_id: str, user_token: str) -> OrderResponse:
        """Get order by ID"""
        # Verify user token
        user_info = await user_service_client.verify_user_token(user_token)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        order = await self.order_repository.get_order_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check if user owns the order (or is admin)
        if order.user_id != user_info["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return await self._convert_to_response(order)
    
    async def get_user_orders(
        self, 
        user_token: str,
        status: Optional[OrderStatus] = None,
        page: int = 1,
        per_page: int = 20
    ) -> OrderListResponse:
        """Get orders for authenticated user"""
        # Verify user token
        user_info = await user_service_client.verify_user_token(user_token)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user_id = user_info["id"]
        offset = (page - 1) * per_page
        
        orders = await self.order_repository.get_orders_by_user(
            user_id=user_id,
            status=status,
            limit=per_page,
            offset=offset
        )
        
        total_orders = await self.order_repository.count_orders(user_id=user_id, status=status)
        total_pages = (total_orders + per_page - 1) // per_page
        
        order_responses = []
        for order in orders:
            order_responses.append(await self._convert_to_response(order))
        
        return OrderListResponse(
            orders=order_responses,
            total=total_orders,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    
    async def update_order_status(
        self, 
        order_id: str, 
        status_update: OrderStatusUpdate
    ) -> OrderResponse:
        """Update order status (admin function)"""
        order = await self.order_repository.update_order_status(
            order_id=order_id,
            status=status_update.status,
            notes=status_update.notes
        )
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Publish appropriate events
        order_event_data = {
            "id": str(order.id),
            "order_number": order.order_number,
            "user_id": order.user_id,
            "user_email": order.user_email,
            "total_amount": order.total_amount,
            "updated_at": order.updated_at.isoformat()
        }
        
        if status_update.status == OrderStatus.CONFIRMED:
            order_event_data["confirmed_at"] = order.confirmed_at.isoformat() if order.confirmed_at else None
            await publish_order_confirmed_event(order_event_data)
        elif status_update.status == OrderStatus.CANCELLED:
            order_event_data["cancellation_reason"] = status_update.notes
            await publish_order_cancelled_event(order_event_data)
        elif status_update.status == OrderStatus.SHIPPED:
            order_event_data.update({
                "shipped_at": order.shipped_at.isoformat() if order.shipped_at else None,
                "tracking_number": order.tracking_number,
                "shipping_method": order.shipping_method,
                "shipping_address": order.shipping_address.dict() if order.shipping_address else None
            })
            await publish_order_shipped_event(order_event_data)
        elif status_update.status == OrderStatus.DELIVERED:
            order_event_data["delivered_at"] = order.delivered_at.isoformat() if order.delivered_at else None
            await publish_order_delivered_event(order_event_data)
        
        return await self._convert_to_response(order)
    
    async def update_payment_status(
        self, 
        order_id: str, 
        payment_update: PaymentUpdate
    ) -> OrderResponse:
        """Update payment status"""
        order = await self.order_repository.update_payment_status(
            order_id=order_id,
            payment_status=payment_update.payment_status,
            payment_transaction_id=payment_update.payment_transaction_id
        )
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Update order fields
        if payment_update.payment_method:
            order.payment_method = payment_update.payment_method
            await order.save()
        
        # Publish payment events
        payment_event_data = {
            "id": str(order.id),
            "order_number": order.order_number,
            "user_id": order.user_id,
            "user_email": order.user_email,
            "total_amount": order.total_amount,
            "payment_method": order.payment_method,
            "payment_transaction_id": order.payment_transaction_id,
            "updated_at": order.updated_at.isoformat()
        }
        
        if payment_update.payment_status == PaymentStatus.PAID:
            await publish_payment_completed_event(payment_event_data)
        elif payment_update.payment_status == PaymentStatus.FAILED:
            payment_event_data["failure_reason"] = "Payment processing failed"
            await publish_payment_failed_event(payment_event_data)
        
        return await self._convert_to_response(order)
    
    async def cancel_order(self, order_id: str, user_token: str) -> OrderResponse:
        """Cancel order (user function)"""
        # Verify user token
        user_info = await user_service_client.verify_user_token(user_token)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        order = await self.order_repository.get_order_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check if user owns the order
        if order.user_id != user_info["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check if order can be cancelled
        if not order.is_cancellable():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order cannot be cancelled in {order.status} status"
            )
        
        # Cancel the order
        cancelled_order = await self.order_repository.update_order_status(
            order_id=order_id,
            status=OrderStatus.CANCELLED,
            notes="Cancelled by customer"
        )
        
        # Publish cancellation event
        order_event_data = {
            "id": str(cancelled_order.id),
            "order_number": cancelled_order.order_number,
            "user_id": cancelled_order.user_id,
            "user_email": cancelled_order.user_email,
            "total_amount": cancelled_order.total_amount,
            "cancellation_reason": "Cancelled by customer",
            "updated_at": cancelled_order.updated_at.isoformat()
        }
        await publish_order_cancelled_event(order_event_data)
        
        return await self._convert_to_response(cancelled_order)
    
    async def get_order_stats(self) -> OrderStats:
        """Get order statistics (admin function)"""
        stats = await self.order_repository.get_order_stats()
        return OrderStats(**stats)
    
    async def _convert_to_response(self, order: Order) -> OrderResponse:
        """Convert Order model to OrderResponse"""
        # Convert items
        items_response = []
        for item in order.items:
            items_response.append({
                "id": str(item.id),
                "product_id": item.product_id,
                "product_name": item.product_name,
                "product_sku": item.product_sku,
                "unit_price": item.unit_price,
                "quantity": item.quantity,
                "total_price": item.total_price,
                "product_snapshot": item.product_snapshot
            })
        
        # Convert shipping address
        shipping_address_response = {
            "id": str(order.shipping_address.id),
            "full_name": order.shipping_address.full_name,
            "address_line_1": order.shipping_address.address_line_1,
            "address_line_2": order.shipping_address.address_line_2,
            "city": order.shipping_address.city,
            "state": order.shipping_address.state,
            "postal_code": order.shipping_address.postal_code,
            "country": order.shipping_address.country,
            "phone": order.shipping_address.phone
        }
        
        return OrderResponse(
            id=str(order.id),
            order_number=order.order_number,
            user_id=order.user_id,
            user_email=order.user_email,
            items=items_response,
            subtotal=order.subtotal,
            tax_amount=order.tax_amount,
            shipping_cost=order.shipping_cost,
            discount_amount=order.discount_amount,
            total_amount=order.total_amount,
            status=order.status,
            payment_status=order.payment_status,
            shipping_address=shipping_address_response,
            shipping_method=order.shipping_method,
            tracking_number=order.tracking_number,
            payment_method=order.payment_method,
            payment_transaction_id=order.payment_transaction_id,
            created_at=order.created_at,
            updated_at=order.updated_at,
            confirmed_at=order.confirmed_at,
            shipped_at=order.shipped_at,
            delivered_at=order.delivered_at,
            notes=order.notes,
            metadata=order.metadata,
            item_count=order.get_item_count(),
            is_editable=order.is_editable(),
            is_cancellable=order.is_cancellable()
        )


