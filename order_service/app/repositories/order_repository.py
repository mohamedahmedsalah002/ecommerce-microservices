from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.order import Order, OrderStatus, PaymentStatus
from beanie.operators import In, And


class OrderRepository:
    """Repository layer for Order data access"""
    
    async def create_order(self, order_data: Dict[str, Any]) -> Order:
        """Create a new order"""
        order = Order(**order_data)
        await order.insert()
        return order
    
    async def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        try:
            return await Order.get(order_id)
        except Exception:
            return None
    
    async def get_order_by_number(self, order_number: str) -> Optional[Order]:
        """Get order by order number"""
        return await Order.find_one({"order_number": order_number})
    
    async def get_orders_by_user(
        self,
        user_id: str,
        status: Optional[OrderStatus] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Order]:
        """Get orders for a specific user"""
        query = {"user_id": user_id}
        
        if status:
            query["status"] = status
        
        orders = await Order.find(query)\
            .sort(-Order.created_at)\
            .skip(offset)\
            .limit(limit)\
            .to_list()
        
        return orders
    
    async def get_orders(
        self,
        status: Optional[OrderStatus] = None,
        payment_status: Optional[PaymentStatus] = None,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Order]:
        """Get orders with optional filtering"""
        query = {}
        
        if status:
            query["status"] = status
        
        if payment_status:
            query["payment_status"] = payment_status
        
        if user_id:
            query["user_id"] = user_id
        
        orders = await Order.find(query)\
            .sort(-Order.created_at)\
            .skip(offset)\
            .limit(limit)\
            .to_list()
        
        return orders
    
    async def update_order(
        self, 
        order_id: str, 
        update_data: Dict[str, Any]
    ) -> Optional[Order]:
        """Update order"""
        try:
            order = await Order.get(order_id)
            if not order:
                return None
            
            # Update timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Update fields
            for key, value in update_data.items():
                setattr(order, key, value)
            
            await order.save()
            return order
            
        except Exception:
            return None
    
    async def update_order_status(
        self,
        order_id: str,
        status: OrderStatus,
        notes: Optional[str] = None
    ) -> Optional[Order]:
        """Update order status with timestamp tracking"""
        try:
            order = await Order.get(order_id)
            if not order:
                return None
            
            # Update status
            order.status = status
            order.updated_at = datetime.utcnow()
            
            # Set status-specific timestamps
            if status == OrderStatus.CONFIRMED and not order.confirmed_at:
                order.confirmed_at = datetime.utcnow()
            elif status == OrderStatus.SHIPPED and not order.shipped_at:
                order.shipped_at = datetime.utcnow()
            elif status == OrderStatus.DELIVERED and not order.delivered_at:
                order.delivered_at = datetime.utcnow()
            
            # Add notes if provided
            if notes:
                if order.notes:
                    order.notes += f"\n{datetime.utcnow().isoformat()}: {notes}"
                else:
                    order.notes = f"{datetime.utcnow().isoformat()}: {notes}"
            
            await order.save()
            return order
            
        except Exception:
            return None
    
    async def update_payment_status(
        self,
        order_id: str,
        payment_status: PaymentStatus,
        payment_transaction_id: Optional[str] = None
    ) -> Optional[Order]:
        """Update payment status"""
        try:
            order = await Order.get(order_id)
            if not order:
                return None
            
            order.payment_status = payment_status
            order.updated_at = datetime.utcnow()
            
            if payment_transaction_id:
                order.payment_transaction_id = payment_transaction_id
            
            await order.save()
            return order
            
        except Exception:
            return None
    
    async def delete_order(self, order_id: str) -> bool:
        """Delete order (soft delete by setting status to cancelled)"""
        try:
            order = await Order.get(order_id)
            if order and order.is_cancellable():
                order.status = OrderStatus.CANCELLED
                order.updated_at = datetime.utcnow()
                await order.save()
                return True
            return False
        except Exception:
            return False
    
    async def count_orders(
        self,
        status: Optional[OrderStatus] = None,
        payment_status: Optional[PaymentStatus] = None,
        user_id: Optional[str] = None
    ) -> int:
        """Count orders with optional filtering"""
        query = {}
        
        if status:
            query["status"] = status
        
        if payment_status:
            query["payment_status"] = payment_status
        
        if user_id:
            query["user_id"] = user_id
        
        return await Order.find(query).count()
    
    async def get_orders_by_status(
        self, 
        statuses: List[OrderStatus], 
        limit: int = 100
    ) -> List[Order]:
        """Get orders by multiple statuses"""
        return await Order.find(In(Order.status, statuses))\
            .sort(Order.created_at)\
            .limit(limit)\
            .to_list()
    
    async def get_orders_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """Get orders within a date range"""
        query = {
            "created_at": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        if status:
            query["status"] = status
        
        return await Order.find(query)\
            .sort(-Order.created_at)\
            .to_list()
    
    async def get_order_stats(self) -> Dict[str, Any]:
        """Get order statistics"""
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                    "total_amount": {"$sum": "$total_amount"}
                }
            }
        ]
        
        result = await Order.aggregate(pipeline).to_list()
        
        stats = {
            "total_orders": 0,
            "pending_orders": 0,
            "confirmed_orders": 0,
            "processing_orders": 0,
            "shipped_orders": 0,
            "delivered_orders": 0,
            "cancelled_orders": 0,
            "total_revenue": 0.0,
            "average_order_value": 0.0
        }
        
        for item in result:
            status = item["_id"]
            count = item["count"]
            total_amount = item["total_amount"]
            
            stats["total_orders"] += count
            
            if status == OrderStatus.PENDING:
                stats["pending_orders"] = count
            elif status == OrderStatus.CONFIRMED:
                stats["confirmed_orders"] = count
            elif status == OrderStatus.PROCESSING:
                stats["processing_orders"] = count
            elif status == OrderStatus.SHIPPED:
                stats["shipped_orders"] = count
            elif status == OrderStatus.DELIVERED:
                stats["delivered_orders"] = count
                stats["total_revenue"] += total_amount
            elif status == OrderStatus.CANCELLED:
                stats["cancelled_orders"] = count
        
        # Calculate average order value
        if stats["total_orders"] > 0:
            total_amount_pipeline = [
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            total_result = await Order.aggregate(total_amount_pipeline).to_list()
            if total_result:
                total_amount = total_result[0]["total"]
                stats["average_order_value"] = round(total_amount / stats["total_orders"], 2)
        
        return stats
    
    async def get_user_order_count(self, user_id: str) -> int:
        """Get total number of orders for a user"""
        return await Order.find({"user_id": user_id}).count()
    
    async def get_recent_orders(self, limit: int = 10) -> List[Order]:
        """Get most recent orders"""
        return await Order.find()\
            .sort(-Order.created_at)\
            .limit(limit)\
            .to_list()


