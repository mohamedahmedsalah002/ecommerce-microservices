# User Service

A microservice for user management with authentication, built with FastAPI, MongoDB, and Beanie ODM following layered architecture principles.

## Architecture

This service follows a layered architecture pattern:

- **Models (M)**: Data models using Beanie ODM for MongoDB
- **Repositories (R)**: Data access layer for MongoDB operations
- **Services (S)**: Business logic layer for user operations
- **Controllers (C)**: FastAPI routes and API endpoints
- **Schemas**: Pydantic models for request/response validation

## Features

- ✅ User registration with email/password
- ✅ JWT-based authentication
- ✅ User profile management
- ✅ Password updates with current password verification
- ✅ Secure password hashing with bcrypt
- ✅ MongoDB integration with Beanie ODM
- ✅ Layered architecture for maintainability
- ✅ Docker support
- ✅ Comprehensive API documentation

## API Endpoints

### Authentication
- `POST /api/v1/users/register` - Register new user
- `POST /api/v1/users/login` - User login

### Profile Management
- `GET /api/v1/users/profile` - Get current user profile
- `PUT /api/v1/users/profile` - Update user profile
- `PATCH /api/v1/users/profile/password` - Update password
- `GET /api/v1/users/profile/{user_id}` - Get user by ID

### System
- `GET /` - Root endpoint
- `GET /health` - Health check

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone and navigate to the user service directory**
2. **Start the services**:
   ```bash
   docker-compose up -d
   ```
3. **Access the API**:
   - User Service: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - MongoDB Admin: http://localhost:8081 (admin/admin123)

### Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up MongoDB** (make sure MongoDB is running on localhost:27017)

3. **Set environment variables**:
   ```bash
   export MONGODB_URL="mongodb://localhost:27017"
   export DATABASE_NAME="ecommerce_users"
   export SECRET_KEY="your-secret-key-here"
   ```

4. **Run the service**:
   ```bash
   cd app
   python main.py
   ```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URL` | `mongodb://localhost:27017` | MongoDB connection URL |
| `DATABASE_NAME` | `ecommerce_users` | Database name |
| `SECRET_KEY` | `your-secret-key-here...` | JWT secret key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT token expiration time |

## Project Structure

```
user_service/
├── app/
│   ├── controllers/          # API routes (FastAPI routers)
│   ├── services/            # Business logic layer
│   ├── repositories/        # Data access layer
│   ├── models/             # Database models (Beanie ODM)
│   ├── schemas/            # Pydantic schemas for API
│   ├── utils/              # Utility functions (auth, etc.)
│   ├── database/           # Database connection
│   └── main.py            # FastAPI application
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## API Usage Examples

### Register User
```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

### Get Profile (requires JWT token)
```bash
curl -X GET "http://localhost:8000/api/v1/users/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Testing

The service includes comprehensive error handling and validation:

- Input validation using Pydantic
- JWT token validation
- Password strength requirements
- Email format validation
- Duplicate email prevention
- Secure password hashing

## Security Features

- Passwords are hashed using bcrypt
- JWT tokens for stateless authentication
- Input validation and sanitization
- CORS middleware configuration
- Non-root user in Docker container

## Development

For development with auto-reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Production Considerations

1. **Change the SECRET_KEY** to a secure random value
2. **Configure CORS** properly for your frontend domains
3. **Use environment variables** for all sensitive configuration
4. **Set up proper logging** and monitoring
5. **Use HTTPS** in production
6. **Configure database connection pooling**
7. **Implement rate limiting** for API endpoints

## Next Steps

This User Service is designed to integrate with:
- Product Service
- Order Service  
- Payment Service
- Notification Service (via Kafka)

Each service will communicate via HTTP APIs and share events through Kafka for decoupled architecture.
