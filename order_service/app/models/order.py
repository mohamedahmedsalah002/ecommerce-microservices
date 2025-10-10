from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal
from beanie import Document
from pydantic import Field, validator
from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class OrderItem(Document):
    """Order item model representing individual products in an order"""
    
    # Product information
    product_id: str = Field(description="Product ID from Product Service")
    product_name: str = Field(description="Product name (cached for performance)")
    product_sku: Optional[str] = Field(None, description="Product SKU")
    
    # Pricing and quantity
    unit_price: float = Field(description="Price per unit at time of order")
    quantity: int = Field(gt=0, description="Quantity ordered")
    total_price: float = Field(description="Total price for this item (unit_price * quantity)")
    
    # Metadata
    product_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Product details at time of order")
    
    class Settings:
        name = "order_items"
    
    @validator('total_price', always=True)
    def calculate_total_price(cls, v, values):
        """Calculate total price based on unit price and quantity"""
        unit_price = values.get('unit_price', 0)
        quantity = values.get('quantity', 0)
        return round(unit_price * quantity, 2)


class ShippingAddress(Document):
    """Shipping address model"""
    
    full_name: str = Field(description="Full name for delivery")
    address_line_1: str = Field(description="Primary address line")
    address_line_2: Optional[str] = Field(None, description="Secondary address line")
    city: str = Field(description="City")
    state: str = Field(description="State/Province")
    postal_code: str = Field(description="Postal/ZIP code")
    country: str = Field(description="Country")
    phone: Optional[str] = Field(None, description="Contact phone number")
    
    class Settings:
        name = "shipping_addresses"


class Order(Document):
    """Order model representing a customer order"""
    
    # Order identification
    order_number: str = Field(description="Unique order number")
    
    # Customer information
    user_id: str = Field(description="User ID from User Service")
    user_email: str = Field(description="User email (cached for performance)")
    
    # Order items
    items: List[OrderItem] = Field(description="List of ordered items")
    
    # Pricing
    subtotal: float = Field(description="Subtotal before taxes and shipping")
    tax_amount: float = Field(default=0.0, description="Tax amount")
    shipping_cost: float = Field(default=0.0, description="Shipping cost")
    discount_amount: float = Field(default=0.0, description="Discount amount")
    total_amount: float = Field(description="Total order amount")
    
    # Status
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Order status")
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Payment status")
    
    # Shipping information
    shipping_address: ShippingAddress = Field(description="Shipping address")
    shipping_method: Optional[str] = Field(None, description="Shipping method")
    tracking_number: Optional[str] = Field(None, description="Shipping tracking number")
    
    # Payment information
    payment_method: Optional[str] = Field(None, description="Payment method")
    payment_transaction_id: Optional[str] = Field(None, description="Payment transaction ID")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = Field(None, description="When order was confirmed")
    shipped_at: Optional[datetime] = Field(None, description="When order was shipped")
    delivered_at: Optional[datetime] = Field(None, description="When order was delivered")
    
    # Metadata
    notes: Optional[str] = Field(None, description="Order notes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Settings:
        name = "orders"
        indexes = [
            "order_number",
            "user_id",
            "status",
            "payment_status",
            "created_at",
            [("user_id", 1), ("status", 1)],
            [("status", 1), ("created_at", -1)],
            [("order_number", 1)]  # Unique index
        ]
    
    @validator('total_amount', always=True)
    def calculate_total_amount(cls, v, values):
        """Calculate total amount"""
        subtotal = values.get('subtotal', 0)
        tax_amount = values.get('tax_amount', 0)
        shipping_cost = values.get('shipping_cost', 0)
        discount_amount = values.get('discount_amount', 0)
        
        total = subtotal + tax_amount + shipping_cost - discount_amount
        return round(max(total, 0), 2)  # Ensure non-negative
    
    @validator('subtotal', always=True)
    def calculate_subtotal(cls, v, values):
        """Calculate subtotal from items"""
        items = values.get('items', [])
        if items:
            return round(sum(item.total_price for item in items), 2)
        return v or 0
    
    def __repr__(self) -> str:
        return f"<Order {self.order_number}: {self.status}>"
    
    def __str__(self) -> str:
        return f"Order({self.order_number}, {self.user_email}, {self.total_amount})"
    
    def is_editable(self) -> bool:
        """Check if order can be edited"""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]
    
    def is_cancellable(self) -> bool:
        """Check if order can be cancelled"""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PROCESSING]
    
    def get_item_count(self) -> int:
        """Get total number of items in the order"""
        return sum(item.quantity for item in self.items)
    
    def get_items_by_product(self, product_id: str) -> List[OrderItem]:
        """Get all items for a specific product"""
        return [item for item in self.items if item.product_id == product_id]


