from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.notification import Notification, NotificationStatus


class NotificationRepository:
    """Repository layer for Notification data access"""
    
    async def create_notification(self, notification_data: Dict[str, Any]) -> Notification:
        """Create a new notification"""
        notification = Notification(**notification_data)
        await notification.insert()
        return notification
    
    async def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID"""
        try:
            return await Notification.get(notification_id)
        except Exception:
            return None
    
    async def get_notifications(
        self,
        recipient: Optional[str] = None,
        status: Optional[NotificationStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications with optional filtering"""
        query = {}
        
        if recipient:
            query["recipient"] = recipient
        
        if status:
            query["status"] = status
        
        notifications = await Notification.find(query)\
            .sort(-Notification.created_at)\
            .skip(offset)\
            .limit(limit)\
            .to_list()
        
        return notifications
    
    async def update_notification(
        self, 
        notification_id: str, 
        update_data: Dict[str, Any]
    ) -> Optional[Notification]:
        """Update notification"""
        try:
            notification = await Notification.get(notification_id)
            if not notification:
                return None
            
            # Update fields
            for key, value in update_data.items():
                setattr(notification, key, value)
            
            await notification.save()
            return notification
            
        except Exception:
            return None
    
    async def delete_notification(self, notification_id: str) -> bool:
        """Delete notification"""
        try:
            notification = await Notification.get(notification_id)
            if notification:
                await notification.delete()
                return True
            return False
        except Exception:
            return False
    
    async def get_notifications_by_event_type(
        self, 
        event_type: str, 
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications by event type"""
        return await Notification.find({"event_type": event_type})\
            .sort(-Notification.created_at)\
            .limit(limit)\
            .to_list()
    
    async def get_pending_notifications(self, limit: int = 100) -> List[Notification]:
        """Get pending notifications for processing"""
        return await Notification.find({"status": NotificationStatus.PENDING})\
            .sort(Notification.created_at)\
            .limit(limit)\
            .to_list()
    
    async def get_failed_notifications(
        self, 
        max_retries: int = 3, 
        limit: int = 100
    ) -> List[Notification]:
        """Get failed notifications that can be retried"""
        return await Notification.find({
            "status": NotificationStatus.FAILED,
            "retry_count": {"$lt": max_retries}
        })\
            .sort(Notification.created_at)\
            .limit(limit)\
            .to_list()
    
    async def count_notifications(
        self,
        recipient: Optional[str] = None,
        status: Optional[NotificationStatus] = None
    ) -> int:
        """Count notifications with optional filtering"""
        query = {}
        
        if recipient:
            query["recipient"] = recipient
        
        if status:
            query["status"] = status
        
        return await Notification.find(query).count()

