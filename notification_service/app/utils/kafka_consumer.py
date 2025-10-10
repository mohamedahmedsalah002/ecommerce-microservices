import os
import json
import logging
import asyncio
from typing import Dict, Any, List
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class KafkaConsumer:
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.kafka_enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
        self.group_id = "notification-service-group"
        self.topics = ["user-events", "product-events"]
        self.consumer = None
        self.notification_service = NotificationService()
        self.running = False
        
    async def start(self):
        """Start the Kafka consumer"""
        if not self.kafka_enabled:
            logger.info("Kafka is disabled, skipping consumer initialization")
            return
            
        try:
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            
            await self.consumer.start()
            self.running = True
            logger.info(f"Kafka consumer started successfully for topics: {self.topics}")
            
            # Start consuming messages in background
            asyncio.create_task(self._consume_messages())
            
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
            self.consumer = None
    
    async def stop(self):
        """Stop the Kafka consumer"""
        self.running = False
        if self.consumer:
            try:
                await self.consumer.stop()
                logger.info("Kafka consumer stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping Kafka consumer: {e}")
    
    async def _consume_messages(self):
        """Consume messages from Kafka topics"""
        if not self.consumer:
            return
            
        try:
            async for message in self.consumer:
                if not self.running:
                    break
                    
                try:
                    await self._process_message(message)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except KafkaError as e:
            logger.error(f"Kafka consumer error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in message consumption: {e}")
    
    async def _process_message(self, message):
        """Process a single Kafka message"""
        try:
            topic = message.topic
            key = message.key
            value = message.value
            
            logger.info(f"Processing message from topic '{topic}' with key '{key}'")
            
            # Extract event data
            service = value.get("service", "unknown")
            event_type = value.get("event_type", "unknown")
            event_data = value.get("data", {})
            
            # Route message to appropriate handler
            if topic == "user-events":
                await self._handle_user_event(event_type, event_data, service)
            elif topic == "product-events":
                await self._handle_product_event(event_type, event_data, service)
            else:
                logger.warning(f"Unknown topic: {topic}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _handle_user_event(self, event_type: str, event_data: Dict[str, Any], service: str):
        """Handle user-related events"""
        try:
            if event_type == "user.registered":
                await self._handle_user_registered(event_data, service)
            elif event_type == "user.login":
                await self._handle_user_login(event_data, service)
            elif event_type == "user.updated":
                await self._handle_user_updated(event_data, service)
            else:
                logger.info(f"Unhandled user event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Error handling user event '{event_type}': {e}")
    
    async def _handle_product_event(self, event_type: str, event_data: Dict[str, Any], service: str):
        """Handle product-related events"""
        try:
            if event_type == "product.created":
                await self._handle_product_created(event_data, service)
            elif event_type == "product.stock_updated":
                await self._handle_product_stock_updated(event_data, service)
            else:
                logger.info(f"Unhandled product event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Error handling product event '{event_type}': {e}")
    
    async def _handle_user_registered(self, event_data: Dict[str, Any], service: str):
        """Handle user registration event"""
        user_email = event_data.get("email")
        user_name = event_data.get("name")
        
        if user_email:
            # Create welcome notification
            notification_data = {
                "type": "email",
                "recipient": user_email,
                "subject": "Welcome to E-commerce Platform!",
                "message": f"Hello {user_name}, welcome to our platform! We're excited to have you on board.",
                "event_type": "user.registered",
                "event_data": event_data,
                "source_service": service,
                "priority": 3
            }
            
            await self.notification_service.create_notification(notification_data)
            logger.info(f"Created welcome notification for user: {user_email}")
    
    async def _handle_user_login(self, event_data: Dict[str, Any], service: str):
        """Handle user login event"""
        # For now, just log the login event
        # In a real system, you might want to send security notifications for suspicious logins
        user_email = event_data.get("email")
        logger.info(f"User login event processed for: {user_email}")
    
    async def _handle_user_updated(self, event_data: Dict[str, Any], service: str):
        """Handle user profile update event"""
        user_email = event_data.get("email")
        logger.info(f"User profile update event processed for: {user_email}")
    
    async def _handle_product_created(self, event_data: Dict[str, Any], service: str):
        """Handle product creation event"""
        product_name = event_data.get("name")
        logger.info(f"Product created event processed for: {product_name}")
        
        # In a real system, you might notify admins or send marketing notifications
    
    async def _handle_product_stock_updated(self, event_data: Dict[str, Any], service: str):
        """Handle product stock update event"""
        product_id = event_data.get("product_id")
        stock_quantity = event_data.get("stock_quantity")
        
        # Send low stock alert if stock is below threshold
        if stock_quantity is not None and stock_quantity < 10:
            notification_data = {
                "type": "email",
                "recipient": "admin@ecommerce.com",  # In real system, get from config
                "subject": "Low Stock Alert",
                "message": f"Product {product_id} has low stock: {stock_quantity} units remaining.",
                "event_type": "product.stock_updated",
                "event_data": event_data,
                "source_service": service,
                "priority": 4
            }
            
            await self.notification_service.create_notification(notification_data)
            logger.info(f"Created low stock alert for product: {product_id}")

# Global consumer instance
kafka_consumer = KafkaConsumer()

