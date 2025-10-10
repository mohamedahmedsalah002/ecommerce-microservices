from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from app.models.order import OrderStatus, PaymentStatus


# Request schemas
class OrderItemCreate(BaseModel):
    """Schema for creating an order item"""
    product_id: str = Field(description="Product ID")
    quantity: int = Field(gt=0, description="Quantity to order")


class ShippingAddressCreate(BaseModel):
    """Schema for creating shipping address"""
    full_name: str = Field(description="Full name for delivery")
    address_line_1: str = Field(description="Primary address line")
    address_line_2: Optional[str] = Field(None, description="Secondary address line")
    city: str = Field(description="City")
    state: str = Field(description="State/Province")
    postal_code: str = Field(description="Postal/ZIP code")
    country: str = Field(description="Country")
    phone: Optional[str] = Field(None, description="Contact phone number")


class OrderCreate(BaseModel):
    """Schema for creating an order"""
    items: List[OrderItemCreate] = Field(description="List of items to order")
    shipping_address: ShippingAddressCreate = Field(description="Shipping address")
    shipping_method: Optional[str] = Field(None, description="Shipping method")
    payment_method: Optional[str] = Field(None, description="Payment method")
    notes: Optional[str] = Field(None, description="Order notes")


class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    status: Optional[OrderStatus] = Field(None, description="Order status")
    payment_status: Optional[PaymentStatus] = Field(None, description="Payment status")
    shipping_method: Optional[str] = Field(None, description="Shipping method")
    tracking_number: Optional[str] = Field(None, description="Tracking number")
    payment_transaction_id: Optional[str] = Field(None, description="Payment transaction ID")
    notes: Optional[str] = Field(None, description="Order notes")


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status"""
    status: OrderStatus = Field(description="New order status")
    notes: Optional[str] = Field(None, description="Status update notes")


class PaymentUpdate(BaseModel):
    """Schema for payment updates"""
    payment_status: PaymentStatus = Field(description="Payment status")
    payment_method: Optional[str] = Field(None, description="Payment method")
    payment_transaction_id: Optional[str] = Field(None, description="Payment transaction ID")


# Response schemas
class OrderItemResponse(BaseModel):
    """Schema for order item response"""
    id: str = Field(description="Item ID")
    product_id: str = Field(description="Product ID")
    product_name: str = Field(description="Product name")
    product_sku: Optional[str] = Field(None, description="Product SKU")
    unit_price: float = Field(description="Unit price")
    quantity: int = Field(description="Quantity")
    total_price: float = Field(description="Total price")
    product_snapshot: Dict[str, Any] = Field(description="Product details snapshot")


class ShippingAddressResponse(BaseModel):
    """Schema for shipping address response"""
    id: str = Field(description="Address ID")
    full_name: str = Field(description="Full name")
    address_line_1: str = Field(description="Primary address line")
    address_line_2: Optional[str] = Field(None, description="Secondary address line")
    city: str = Field(description="City")
    state: str = Field(description="State/Province")
    postal_code: str = Field(description="Postal/ZIP code")
    country: str = Field(description="Country")
    phone: Optional[str] = Field(None, description="Phone number")


class OrderResponse(BaseModel):
    """Schema for order response"""
    id: str = Field(description="Order ID")
    order_number: str = Field(description="Order number")
    user_id: str = Field(description="User ID")
    user_email: str = Field(description="User email")
    
    items: List[OrderItemResponse] = Field(description="Order items")
    
    subtotal: float = Field(description="Subtotal")
    tax_amount: float = Field(description="Tax amount")
    shipping_cost: float = Field(description="Shipping cost")
    discount_amount: float = Field(description="Discount amount")
    total_amount: float = Field(description="Total amount")
    
    status: OrderStatus = Field(description="Order status")
    payment_status: PaymentStatus = Field(description="Payment status")
    
    shipping_address: ShippingAddressResponse = Field(description="Shipping address")
    shipping_method: Optional[str] = Field(None, description="Shipping method")
    tracking_number: Optional[str] = Field(None, description="Tracking number")
    
    payment_method: Optional[str] = Field(None, description="Payment method")
    payment_transaction_id: Optional[str] = Field(None, description="Payment transaction ID")
    
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    confirmed_at: Optional[datetime] = Field(None, description="Confirmation timestamp")
    shipped_at: Optional[datetime] = Field(None, description="Shipping timestamp")
    delivered_at: Optional[datetime] = Field(None, description="Delivery timestamp")
    
    notes: Optional[str] = Field(None, description="Order notes")
    metadata: Dict[str, Any] = Field(description="Additional metadata")
    
    # Computed fields
    item_count: int = Field(description="Total number of items")
    is_editable: bool = Field(description="Whether order can be edited")
    is_cancellable: bool = Field(description="Whether order can be cancelled")


class OrderListResponse(BaseModel):
    """Schema for order list response"""
    orders: List[OrderResponse] = Field(description="List of orders")
    total: int = Field(description="Total number of orders")
    page: int = Field(description="Current page")
    per_page: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")


class OrderSummary(BaseModel):
    """Schema for order summary"""
    id: str = Field(description="Order ID")
    order_number: str = Field(description="Order number")
    status: OrderStatus = Field(description="Order status")
    payment_status: PaymentStatus = Field(description="Payment status")
    total_amount: float = Field(description="Total amount")
    item_count: int = Field(description="Number of items")
    created_at: datetime = Field(description="Creation timestamp")


class OrderStats(BaseModel):
    """Schema for order statistics"""
    total_orders: int = Field(description="Total number of orders")
    pending_orders: int = Field(description="Number of pending orders")
    confirmed_orders: int = Field(description="Number of confirmed orders")
    processing_orders: int = Field(description="Number of processing orders")
    shipped_orders: int = Field(description="Number of shipped orders")
    delivered_orders: int = Field(description="Number of delivered orders")
    cancelled_orders: int = Field(description="Number of cancelled orders")
    total_revenue: float = Field(description="Total revenue from completed orders")
    average_order_value: float = Field(description="Average order value")


