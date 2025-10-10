from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from typing import Optional, List
from app.services.order_service import OrderService
from app.schemas.order_schemas import (
    OrderCreate, OrderResponse, OrderListResponse, OrderStats,
    OrderStatusUpdate, PaymentUpdate, OrderSummary
)
from app.models.order import OrderStatus, PaymentStatus

# Create router
router = APIRouter(prefix="/api/v1/orders", tags=["orders"])

# Dependency to get order service
def get_order_service() -> OrderService:
    return OrderService()

# Dependency to get authorization token
def get_auth_token(authorization: str = Header(...)) -> str:
    """Extract Bearer token from Authorization header"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    return authorization.split(" ")[1]


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    token: str = Depends(get_auth_token),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Create a new order
    
    - **items**: List of products and quantities to order
    - **shipping_address**: Delivery address
    - **shipping_method**: Preferred shipping method
    - **payment_method**: Payment method
    - **notes**: Optional order notes
    """
    return await order_service.create_order(order_data, token)


@router.get("/", response_model=OrderListResponse)
async def get_user_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    token: str = Depends(get_auth_token),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Get orders for the authenticated user
    
    - **status**: Optional filter by order status
    - **page**: Page number for pagination
    - **per_page**: Number of orders per page
    """
    return await order_service.get_user_orders(
        user_token=token,
        status=status,
        page=page,
        per_page=per_page
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    token: str = Depends(get_auth_token),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Get a specific order by ID
    
    - **order_id**: The order ID to retrieve
    """
    return await order_service.get_order_by_id(order_id, token)


@router.patch("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    token: str = Depends(get_auth_token),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Cancel an order
    
    - **order_id**: The order ID to cancel
    
    Only orders in pending, confirmed, or processing status can be cancelled.
    """
    return await order_service.cancel_order(order_id, token)


# Admin endpoints (would typically require admin authentication)
@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Update order status (Admin only)
    
    - **order_id**: The order ID to update
    - **status**: New order status
    - **notes**: Optional notes about the status change
    """
    return await order_service.update_order_status(order_id, status_update)


@router.patch("/{order_id}/payment", response_model=OrderResponse)
async def update_payment_status(
    order_id: str,
    payment_update: PaymentUpdate,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Update payment status (Admin/Payment processor only)
    
    - **order_id**: The order ID to update
    - **payment_status**: New payment status
    - **payment_method**: Payment method used
    - **payment_transaction_id**: Transaction ID from payment processor
    """
    return await order_service.update_payment_status(order_id, payment_update)


@router.get("/admin/stats", response_model=OrderStats)
async def get_order_statistics(
    order_service: OrderService = Depends(get_order_service)
):
    """
    Get order statistics (Admin only)
    
    Returns comprehensive statistics about orders including:
    - Total orders by status
    - Revenue metrics
    - Average order value
    """
    return await order_service.get_order_stats()


@router.get("/admin/all", response_model=OrderListResponse)
async def get_all_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    payment_status: Optional[PaymentStatus] = Query(None, description="Filter by payment status"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Get all orders with filtering (Admin only)
    
    - **status**: Optional filter by order status
    - **payment_status**: Optional filter by payment status
    - **user_id**: Optional filter by user ID
    - **page**: Page number for pagination
    - **per_page**: Number of orders per page
    """
    from app.repositories.order_repository import OrderRepository
    
    repository = OrderRepository()
    offset = (page - 1) * per_page
    
    orders = await repository.get_orders(
        status=status,
        payment_status=payment_status,
        user_id=user_id,
        limit=per_page,
        offset=offset
    )
    
    total_orders = await repository.count_orders(
        status=status,
        payment_status=payment_status,
        user_id=user_id
    )
    
    total_pages = (total_orders + per_page - 1) // per_page
    
    # Convert to response format
    order_responses = []
    for order in orders:
        order_service_instance = OrderService()
        order_response = await order_service_instance._convert_to_response(order)
        order_responses.append(order_response)
    
    return OrderListResponse(
        orders=order_responses,
        total=total_orders,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


# Health and utility endpoints
@router.get("/health/check")
async def health_check():
    """Health check endpoint for the order service"""
    return {
        "status": "healthy",
        "service": "order-service",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@router.get("/status/options")
async def get_status_options():
    """Get available order and payment status options"""
    return {
        "order_statuses": [status.value for status in OrderStatus],
        "payment_statuses": [status.value for status in PaymentStatus]
    }


