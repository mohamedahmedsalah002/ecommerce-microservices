from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.utils.kafka_consumer import kafka_consumer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Notification Service...")
    await connect_to_mongo()
    await kafka_consumer.start()
    logger.info("Notification Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Notification Service...")
    await kafka_consumer.stop()
    await close_mongo_connection()
    logger.info("Notification Service shut down successfully")


# Create FastAPI application
app = FastAPI(
    title="Notification Service API",
    description="Microservice for handling notifications and events",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Notification Service API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "notification-service"}


@app.get("/api/v1/notifications/stats")
async def get_notification_stats():
    """Get notification statistics"""
    from app.repositories.notification_repository import NotificationRepository
    from app.models.notification import NotificationStatus
    
    repo = NotificationRepository()
    
    try:
        stats = {
            "total": await repo.count_notifications(),
            "pending": await repo.count_notifications(status=NotificationStatus.PENDING),
            "sent": await repo.count_notifications(status=NotificationStatus.SENT),
            "delivered": await repo.count_notifications(status=NotificationStatus.DELIVERED),
            "failed": await repo.count_notifications(status=NotificationStatus.FAILED)
        }
        
        return {"success": True, "data": stats}
        
    except Exception as e:
        logger.error(f"Error getting notification stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/notifications")
async def get_notifications(
    recipient: str = None,
    status: str = None,
    limit: int = 50,
    offset: int = 0
):
    """Get notifications with optional filtering"""
    from app.services.notification_service import NotificationService
    from app.models.notification import NotificationStatus
    
    service = NotificationService()
    
    try:
        # Validate status if provided
        notification_status = None
        if status:
            try:
                notification_status = NotificationStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        notifications = await service.get_notifications(
            recipient=recipient,
            status=notification_status,
            limit=limit,
            offset=offset
        )
        
        # Convert to dict for JSON response
        notifications_data = []
        for notification in notifications:
            notification_dict = notification.dict()
            notification_dict["id"] = str(notification.id)
            notifications_data.append(notification_dict)
        
        return {
            "success": True,
            "data": notifications_data,
            "count": len(notifications_data),
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/v1/notifications/retry-failed")
async def retry_failed_notifications():
    """Retry failed notifications"""
    from app.services.notification_service import NotificationService
    
    service = NotificationService()
    
    try:
        retry_count = await service.retry_failed_notifications()
        
        return {
            "success": True,
            "message": f"Retried {retry_count} failed notifications",
            "retry_count": retry_count
        }
        
    except Exception as e:
        logger.error(f"Error retrying failed notifications: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    from fastapi.responses import JSONResponse
    import traceback
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )

