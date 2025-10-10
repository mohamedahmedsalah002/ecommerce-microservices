import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.repositories.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)

class NotificationService:
    """Service layer for Notification business logic"""
    
    def __init__(self):
        self.notification_repository = NotificationRepository()
    
    async def create_notification(self, notification_data: Dict[str, Any]) -> Notification:
        """Create a new notification"""
        try:
            # Validate notification type
            notification_type = notification_data.get("type")
            if notification_type not in [t.value for t in NotificationType]:
                raise ValueError(f"Invalid notification type: {notification_type}")
            
            # Create notification
            notification = await self.notification_repository.create_notification(notification_data)
            
            # Attempt to send the notification immediately
            await self._send_notification(notification)
            
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            raise
    
    async def get_notifications(
        self, 
        recipient: Optional[str] = None,
        status: Optional[NotificationStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications with optional filtering"""
        return await self.notification_repository.get_notifications(
            recipient=recipient,
            status=status,
            limit=limit,
            offset=offset
        )
    
    async def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID"""
        return await self.notification_repository.get_notification_by_id(notification_id)
    
    async def update_notification_status(
        self, 
        notification_id: str, 
        status: NotificationStatus,
        delivered_at: Optional[datetime] = None
    ) -> Optional[Notification]:
        """Update notification status"""
        update_data = {"status": status, "updated_at": datetime.utcnow()}
        
        if status == NotificationStatus.SENT:
            update_data["sent_at"] = datetime.utcnow()
        elif status == NotificationStatus.DELIVERED and delivered_at:
            update_data["delivered_at"] = delivered_at
        
        return await self.notification_repository.update_notification(notification_id, update_data)
    
    async def retry_failed_notifications(self, max_retries: int = 3) -> int:
        """Retry failed notifications that haven't exceeded max retries"""
        failed_notifications = await self.notification_repository.get_notifications(
            status=NotificationStatus.FAILED,
            limit=100
        )
        
        retry_count = 0
        for notification in failed_notifications:
            if notification.retry_count < max_retries:
                try:
                    await self._send_notification(notification)
                    retry_count += 1
                except Exception as e:
                    logger.error(f"Failed to retry notification {notification.id}: {e}")
        
        return retry_count
    
    async def _send_notification(self, notification: Notification):
        """Send a notification based on its type"""
        try:
            if notification.type == NotificationType.EMAIL:
                await self._send_email_notification(notification)
            elif notification.type == NotificationType.SMS:
                await self._send_sms_notification(notification)
            elif notification.type == NotificationType.PUSH:
                await self._send_push_notification(notification)
            elif notification.type == NotificationType.IN_APP:
                await self._send_in_app_notification(notification)
            else:
                raise ValueError(f"Unsupported notification type: {notification.type}")
                
        except Exception as e:
            # Update notification status to failed
            await self.update_notification_status(
                str(notification.id), 
                NotificationStatus.FAILED
            )
            
            # Increment retry count
            await self.notification_repository.update_notification(
                str(notification.id),
                {
                    "retry_count": notification.retry_count + 1,
                    "updated_at": datetime.utcnow()
                }
            )
            
            logger.error(f"Failed to send notification {notification.id}: {e}")
            raise
    
    async def _send_email_notification(self, notification: Notification):
        """Send email notification (mock implementation)"""
        # In a real implementation, you would integrate with an email service
        # like SendGrid, AWS SES, or SMTP
        
        logger.info(f"Sending email to {notification.recipient}")
        logger.info(f"Subject: {notification.subject}")
        logger.info(f"Message: {notification.message}")
        
        # Mock successful sending
        await self.update_notification_status(
            str(notification.id),
            NotificationStatus.SENT
        )
        
        # Simulate delivery confirmation (in real system, this would come from email provider)
        await self.update_notification_status(
            str(notification.id),
            NotificationStatus.DELIVERED,
            datetime.utcnow()
        )
        
        logger.info(f"Email notification {notification.id} sent successfully")
    
    async def _send_sms_notification(self, notification: Notification):
        """Send SMS notification (mock implementation)"""
        # In a real implementation, you would integrate with an SMS service
        # like Twilio, AWS SNS, or similar
        
        logger.info(f"Sending SMS to {notification.recipient}")
        logger.info(f"Message: {notification.message}")
        
        # Mock successful sending
        await self.update_notification_status(
            str(notification.id),
            NotificationStatus.SENT
        )
        
        logger.info(f"SMS notification {notification.id} sent successfully")
    
    async def _send_push_notification(self, notification: Notification):
        """Send push notification (mock implementation)"""
        # In a real implementation, you would integrate with push notification services
        # like Firebase Cloud Messaging, Apple Push Notification Service, etc.
        
        logger.info(f"Sending push notification to {notification.recipient}")
        logger.info(f"Message: {notification.message}")
        
        # Mock successful sending
        await self.update_notification_status(
            str(notification.id),
            NotificationStatus.SENT
        )
        
        logger.info(f"Push notification {notification.id} sent successfully")
    
    async def _send_in_app_notification(self, notification: Notification):
        """Send in-app notification (mock implementation)"""
        # In a real implementation, you would store this in a user's notification inbox
        # or send via WebSocket to connected clients
        
        logger.info(f"Creating in-app notification for {notification.recipient}")
        logger.info(f"Message: {notification.message}")
        
        # Mock successful sending
        await self.update_notification_status(
            str(notification.id),
            NotificationStatus.SENT
        )
        
        logger.info(f"In-app notification {notification.id} created successfully")

