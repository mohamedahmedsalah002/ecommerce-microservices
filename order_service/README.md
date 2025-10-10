# Order Service

A comprehensive order management microservice built with FastAPI, MongoDB, and Kafka for event-driven architecture.

## Features

- ✅ **Order Management** - Create, update, and track orders
- ✅ **Order Status Tracking** - Complete order lifecycle management
- ✅ **Payment Integration** - Payment status tracking and updates
- ✅ **Product Integration** - Real-time product availability checking
- ✅ **User Authentication** - JWT-based user verification
- ✅ **Event-Driven Architecture** - Kafka integration for order events
- ✅ **Comprehensive API** - RESTful endpoints with OpenAPI documentation
- ✅ **Database Integration** - MongoDB with Beanie ODM
- ✅ **Docker Support** - Containerized deployment

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **MongoDB** - NoSQL database for flexible data storage
- **Beanie** - Async MongoDB ODM based on Pydantic
- **Kafka** - Event streaming platform for microservices communication
- **Docker** - Containerization for easy deployment
- **Pydantic** - Data validation and settings management

## API Endpoints

### Order Management
- `POST /api/v1/orders/` - Create a new order
- `GET /api/v1/orders/` - Get user's orders with pagination
- `GET /api/v1/orders/{order_id}` - Get specific order details
- `PATCH /api/v1/orders/{order_id}/cancel` - Cancel an order

### Admin Endpoints
- `PATCH /api/v1/orders/{order_id}/status` - Update order status
- `PATCH /api/v1/orders/{order_id}/payment` - Update payment status
- `GET /api/v1/orders/admin/stats` - Get order statistics
- `GET /api/v1/orders/admin/all` - Get all orders with filtering

### Utility Endpoints
- `GET /health` - Health check
- `GET /api/v1/orders/status/options` - Get available status options

## Order Lifecycle

1. **Pending** - Order created, awaiting confirmation
2. **Confirmed** - Order confirmed, payment processing
3. **Processing** - Order being prepared for shipment
4. **Shipped** - Order shipped, tracking available
5. **Delivered** - Order successfully delivered
6. **Cancelled** - Order cancelled by user or system
7. **Refunded** - Order refunded

## Payment Status

- **Pending** - Payment not yet processed
- **Paid** - Payment successfully completed
- **Failed** - Payment processing failed
- **Refunded** - Payment refunded to customer

## Event-Driven Architecture

The Order Service publishes events to Kafka topics for other services to consume:

### Published Events
- `order.created` - New order created
- `order.confirmed` - Order confirmed
- `order.cancelled` - Order cancelled
- `order.shipped` - Order shipped with tracking
- `order.delivered` - Order delivered
- `order.payment_completed` - Payment successful
- `order.payment_failed` - Payment failed

## Data Models

### Order
- Order identification and numbering
- Customer information
- Order items with product details
- Pricing breakdown (subtotal, tax, shipping, discounts)
- Status tracking
- Shipping information
- Payment details
- Timestamps for lifecycle events

### OrderItem
- Product information snapshot
- Quantity and pricing
- Product metadata at time of order

### ShippingAddress
- Complete delivery address
- Contact information

## External Service Integration

### User Service Integration
- JWT token verification
- User profile retrieval
- Authorization checks

### Product Service Integration
- Product availability checking
- Product information retrieval
- Stock reservation (planned)
- Price validation

## Environment Variables

```bash
MONGODB_URL=mongodb://order-mongodb:27017
DATABASE_NAME=ecommerce_orders
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
KAFKA_ENABLED=true
USER_SERVICE_URL=http://user-service:8000
PRODUCT_SERVICE_URL=http://product-service:8001
```

## Getting Started

### Prerequisites
- Docker and Docker Compose
- User Service running on port 8000
- Product Service running on port 8001
- Kafka infrastructure

### Running the Service

1. **Build and start with Docker Compose**:
   ```bash
   docker compose up --build order-service
   ```

2. **Access the API**:
   - Service: http://localhost:8003
   - Documentation: http://localhost:8003/docs
   - Health Check: http://localhost:8003/health

### Testing the API

1. **Create an order** (requires authentication):
   ```bash
   curl -X POST "http://localhost:8003/api/v1/orders/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "items": [
         {
           "product_id": "product_id_here",
           "quantity": 2
         }
       ],
       "shipping_address": {
         "full_name": "John Doe",
         "address_line_1": "123 Main St",
         "city": "Anytown",
         "state": "CA",
         "postal_code": "12345",
         "country": "USA"
       },
       "shipping_method": "standard",
       "payment_method": "credit_card"
     }'
   ```

2. **Get user orders**:
   ```bash
   curl -X GET "http://localhost:8003/api/v1/orders/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

3. **Get order statistics** (admin):
   ```bash
   curl -X GET "http://localhost:8003/api/v1/orders/admin/stats"
   ```

## Database Schema

### Collections
- `orders` - Main order documents
- `order_items` - Individual order items (embedded in orders)
- `shipping_addresses` - Shipping address documents

### Indexes
- Order number (unique)
- User ID + Status
- Status + Created date
- Payment status

## Error Handling

The service provides comprehensive error handling with appropriate HTTP status codes:

- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Invalid or missing authentication
- `403 Forbidden` - Access denied
- `404 Not Found` - Order not found
- `500 Internal Server Error` - Server errors

## Monitoring and Observability

- Health check endpoint for service monitoring
- Comprehensive logging for debugging
- Kafka event publishing for order tracking
- Database connection monitoring

## Security Features

- JWT token validation
- User authorization checks
- Input validation and sanitization
- Secure database connections
- CORS configuration

## Future Enhancements

- [ ] Order modification capabilities
- [ ] Bulk order operations
- [ ] Advanced order search and filtering
- [ ] Order templates and recurring orders
- [ ] Integration with shipping providers
- [ ] Real-time order tracking
- [ ] Order analytics and reporting
- [ ] Inventory reservation system
- [ ] Multi-currency support
- [ ] Order workflow customization


