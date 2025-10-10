# Product Service

A microservice for product and category management with comprehensive CRUD operations, built with FastAPI, MongoDB, and Beanie ODM following layered architecture principles.

## Architecture

This service follows a layered architecture pattern:

- **Models (M)**: Data models using Beanie ODM for MongoDB (Product, Category)
- **Repositories (R)**: Data access layer for MongoDB operations
- **Services (S)**: Business logic layer for product and category operations
- **Controllers (C)**: FastAPI routes and API endpoints
- **Schemas**: Pydantic models for request/response validation

## Features

- ✅ **Category Management** - Create, read, update, delete categories
- ✅ **Product CRUD** - Complete product lifecycle management
- ✅ **Advanced Search** - Search products by name, description, tags, price range
- ✅ **Category Filtering** - Filter products by category
- ✅ **Stock Management** - Track and update product inventory
- ✅ **Image Support** - Multiple image URLs per product
- ✅ **Tagging System** - Flexible product tagging
- ✅ **Pagination** - Efficient data retrieval with pagination
- ✅ **Soft Delete** - Products and categories are deactivated, not deleted
- ✅ **Data Validation** - Comprehensive input validation with Pydantic

## API Endpoints

### Categories
- `POST /api/v1/categories/` - Create new category
- `GET /api/v1/categories/` - Get all categories (with pagination)
- `GET /api/v1/categories/{category_id}` - Get category by ID
- `PUT /api/v1/categories/{category_id}` - Update category
- `DELETE /api/v1/categories/{category_id}` - Delete category (soft delete)

### Products
- `POST /api/v1/products/` - Create new product
- `GET /api/v1/products/` - Get all products (with pagination)
- `GET /api/v1/products/search` - Search products with filters
- `GET /api/v1/products/{product_id}` - Get product by ID
- `PUT /api/v1/products/{product_id}` - Update product
- `DELETE /api/v1/products/{product_id}` - Delete product (soft delete)
- `PATCH /api/v1/products/{product_id}/stock` - Update product stock

### System
- `GET /` - Root endpoint
- `GET /health` - Health check

## Quick Start

### Using Docker Compose (Recommended)

1. **Navigate to the product service directory**
2. **Start the services**:
   ```bash
   docker compose up -d
   ```
3. **Access the API**:
   - Product Service: http://localhost:8001
   - API Documentation: http://localhost:8001/docs
   - MongoDB Admin: http://localhost:8082 (admin/admin123)

### Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up MongoDB** (make sure MongoDB is running on localhost:27018)

3. **Set environment variables**:
   ```bash
   export MONGODB_URL="mongodb://localhost:27018"
   export DATABASE_NAME="ecommerce_products"
   ```

4. **Run the service**:
   ```bash
   cd app
   python main.py
   ```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URL` | `mongodb://localhost:27018` | MongoDB connection URL |
| `DATABASE_NAME` | `ecommerce_products` | Database name |
| `DEBUG` | `True` | Debug mode |
| `HOST` | `0.0.0.0` | Host address |
| `PORT` | `8001` | Service port |

## Data Models

### Product
```json
{
  "name": "iPhone 15 Pro",
  "description": "Latest iPhone with advanced camera system",
  "price": 999.99,
  "category_id": "category_id_here",
  "sku": "IPH15PRO128",
  "stock_quantity": 50,
  "is_available": true,
  "image_urls": ["https://example.com/image.jpg"],
  "tags": ["smartphone", "apple", "electronics"],
  "weight": 0.221,
  "dimensions": {"length": 14.67, "width": 7.09, "height": 0.83}
}
```

### Category
```json
{
  "name": "Electronics",
  "description": "Electronic devices and accessories"
}
```

## API Usage Examples

### Create Category
```bash
curl -X POST "http://localhost:8001/api/v1/categories/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electronics",
    "description": "Electronic devices and accessories"
  }'
```

### Create Product
```bash
curl -X POST "http://localhost:8001/api/v1/products/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPhone 15 Pro",
    "description": "Latest iPhone with advanced camera system and A17 Pro chip",
    "price": 999.99,
    "category_id": "category_id_here",
    "sku": "IPH15PRO128",
    "stock_quantity": 50,
    "tags": ["smartphone", "apple", "electronics"]
  }'
```

### Search Products
```bash
curl "http://localhost:8001/api/v1/products/search?query=iphone&min_price=500&max_price=1500&page=1&per_page=10"
```

### Update Stock
```bash
curl -X PATCH "http://localhost:8001/api/v1/products/{product_id}/stock?quantity_change=-5"
```

## Project Structure

```
product_service/
├── app/
│   ├── controllers/          # API routes (FastAPI routers)
│   ├── services/            # Business logic layer
│   ├── repositories/        # Data access layer
│   ├── models/             # Database models (Beanie ODM)
│   ├── schemas/            # Pydantic schemas for API
│   ├── database/           # Database connection
│   └── main.py            # FastAPI application
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── init-mongo.js
└── README.md
```

## Search & Filtering Features

The Product Service provides powerful search and filtering capabilities:

- **Text Search**: Search in product names, descriptions, and tags
- **Category Filtering**: Filter by specific categories
- **Price Range**: Filter by minimum and maximum price
- **Tag Filtering**: Filter by multiple tags
- **Availability**: Filter by stock availability
- **Pagination**: Efficient pagination for large datasets

## Integration Ready

This Product Service is designed to integrate seamlessly with:
- **User Service** - For user authentication and authorization
- **Order Service** - For product selection and inventory management
- **Payment Service** - For product pricing information
- **Notification Service** - For product update notifications

The service follows REST API standards and provides comprehensive error handling, making it easy to integrate with frontend applications and other microservices.


