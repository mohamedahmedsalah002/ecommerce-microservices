from datetime import datetime
from typing import Optional, Dict, Any
from beanie import Document
from pydantic import Field
from enum import Enum


class NotificationType(str, Enum):
    """Notification types"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(str, Enum):
    """Notification status"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"


class Notification(Document):
    """Notification model"""
    
    # Basic information
    type: NotificationType = Field(description="Type of notification")
    recipient: str = Field(description="Recipient identifier (email, phone, user_id)")
    subject: Optional[str] = Field(None, description="Notification subject")
    message: str = Field(description="Notification message content")
    
    # Status and tracking
    status: NotificationStatus = Field(default=NotificationStatus.PENDING)
    sent_at: Optional[datetime] = Field(None, description="When notification was sent")
    delivered_at: Optional[datetime] = Field(None, description="When notification was delivered")
    
    # Event information
    event_type: str = Field(description="Type of event that triggered this notification")
    event_data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    source_service: str = Field(description="Service that generated the event")
    
    # Metadata
    template_id: Optional[str] = Field(None, description="Template used for notification")
    priority: int = Field(default=1, description="Notification priority (1=low, 5=high)")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "notifications"
        indexes = [
            "recipient",
            "status",
            "event_type",
            "created_at",
            [("recipient", 1), ("status", 1)],
            [("event_type", 1), ("created_at", -1)]
        ]
    
    def __repr__(self) -> str:
        return f"<Notification {self.id}: {self.type} to {self.recipient}>"
    
    def __str__(self) -> str:
        return f"Notification({self.type}, {self.recipient}, {self.status})"

