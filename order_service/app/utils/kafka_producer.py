import os
import json
import logging
from typing import Dict, Any, Optional
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

logger = logging.getLogger(__name__)

class KafkaProducer:
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.kafka_enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
        self.producer: Optional[AIOKafkaProducer] = None
        
    async def start(self):
        """Start the Kafka producer"""
        if not self.kafka_enabled:
            logger.info("Kafka is disabled, skipping producer initialization")
            return
            
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                retry_backoff_ms=1000,
                request_timeout_ms=30000,
                enable_idempotence=True
            )
            await self.producer.start()
            logger.info(f"Kafka producer started successfully with servers: {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            self.producer = None
    
    async def stop(self):
        """Stop the Kafka producer"""
        if self.producer:
            try:
                await self.producer.stop()
                logger.info("Kafka producer stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping Kafka producer: {e}")
    
    async def send_event(self, topic: str, event_data: Dict[str, Any], key: Optional[str] = None):
        """Send an event to a Kafka topic"""
        if not self.kafka_enabled or not self.producer:
            logger.debug(f"Kafka disabled or producer not available, skipping event: {topic}")
            return
        
        try:
            # Add metadata to the event
            enriched_event = {
                "service": "order-service",
                "timestamp": event_data.get("timestamp"),
                "event_type": topic,
                "data": event_data
            }
            
            # Send the message
            await self.producer.send_and_wait(topic, enriched_event, key=key)
            logger.info(f"Event sent to topic '{topic}': {event_data.get('event_type', 'unknown')}")
            
        except KafkaError as e:
            logger.error(f"Kafka error sending event to topic '{topic}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending event to topic '{topic}': {e}")

# Global producer instance
kafka_producer = KafkaProducer()

# Event types for order service
class OrderEvents:
    ORDER_CREATED = "order.created"
    ORDER_CONFIRMED = "order.confirmed"
    ORDER_CANCELLED = "order.cancelled"
    ORDER_SHIPPED = "order.shipped"
    ORDER_DELIVERED = "order.delivered"
    ORDER_PAYMENT_COMPLETED = "order.payment_completed"
    ORDER_PAYMENT_FAILED = "order.payment_failed"
    ORDER_REFUNDED = "order.refunded"

# Helper functions for common events
async def publish_order_created_event(order_data: Dict[str, Any]):
    """Publish order created event"""
    event_data = {
        "event_type": OrderEvents.ORDER_CREATED,
        "order_id": order_data.get("id"),
        "order_number": order_data.get("order_number"),
        "user_id": order_data.get("user_id"),
        "user_email": order_data.get("user_email"),
        "total_amount": order_data.get("total_amount"),
        "item_count": order_data.get("item_count"),
        "items": order_data.get("items", []),
        "timestamp": order_data.get("created_at")
    }
    await kafka_producer.send_event("order-events", event_data, key=order_data.get("id"))

async def publish_order_confirmed_event(order_data: Dict[str, Any]):
    """Publish order confirmed event"""
    event_data = {
        "event_type": OrderEvents.ORDER_CONFIRMED,
        "order_id": order_data.get("id"),
        "order_number": order_data.get("order_number"),
        "user_id": order_data.get("user_id"),
        "user_email": order_data.get("user_email"),
        "total_amount": order_data.get("total_amount"),
        "items": order_data.get("items", []),
        "timestamp": order_data.get("confirmed_at")
    }
    await kafka_producer.send_event("order-events", event_data, key=order_data.get("id"))

async def publish_order_cancelled_event(order_data: Dict[str, Any]):
    """Publish order cancelled event"""
    event_data = {
        "event_type": OrderEvents.ORDER_CANCELLED,
        "order_id": order_data.get("id"),
        "order_number": order_data.get("order_number"),
        "user_id": order_data.get("user_id"),
        "user_email": order_data.get("user_email"),
        "total_amount": order_data.get("total_amount"),
        "reason": order_data.get("cancellation_reason"),
        "timestamp": order_data.get("updated_at")
    }
    await kafka_producer.send_event("order-events", event_data, key=order_data.get("id"))

async def publish_order_shipped_event(order_data: Dict[str, Any]):
    """Publish order shipped event"""
    event_data = {
        "event_type": OrderEvents.ORDER_SHIPPED,
        "order_id": order_data.get("id"),
        "order_number": order_data.get("order_number"),
        "user_id": order_data.get("user_id"),
        "user_email": order_data.get("user_email"),
        "tracking_number": order_data.get("tracking_number"),
        "shipping_method": order_data.get("shipping_method"),
        "shipping_address": order_data.get("shipping_address"),
        "timestamp": order_data.get("shipped_at")
    }
    await kafka_producer.send_event("order-events", event_data, key=order_data.get("id"))

async def publish_order_delivered_event(order_data: Dict[str, Any]):
    """Publish order delivered event"""
    event_data = {
        "event_type": OrderEvents.ORDER_DELIVERED,
        "order_id": order_data.get("id"),
        "order_number": order_data.get("order_number"),
        "user_id": order_data.get("user_id"),
        "user_email": order_data.get("user_email"),
        "total_amount": order_data.get("total_amount"),
        "timestamp": order_data.get("delivered_at")
    }
    await kafka_producer.send_event("order-events", event_data, key=order_data.get("id"))

async def publish_payment_completed_event(order_data: Dict[str, Any]):
    """Publish payment completed event"""
    event_data = {
        "event_type": OrderEvents.ORDER_PAYMENT_COMPLETED,
        "order_id": order_data.get("id"),
        "order_number": order_data.get("order_number"),
        "user_id": order_data.get("user_id"),
        "user_email": order_data.get("user_email"),
        "total_amount": order_data.get("total_amount"),
        "payment_method": order_data.get("payment_method"),
        "payment_transaction_id": order_data.get("payment_transaction_id"),
        "timestamp": order_data.get("updated_at")
    }
    await kafka_producer.send_event("order-events", event_data, key=order_data.get("id"))

async def publish_payment_failed_event(order_data: Dict[str, Any]):
    """Publish payment failed event"""
    event_data = {
        "event_type": OrderEvents.ORDER_PAYMENT_FAILED,
        "order_id": order_data.get("id"),
        "order_number": order_data.get("order_number"),
        "user_id": order_data.get("user_id"),
        "user_email": order_data.get("user_email"),
        "total_amount": order_data.get("total_amount"),
        "payment_method": order_data.get("payment_method"),
        "failure_reason": order_data.get("failure_reason"),
        "timestamp": order_data.get("updated_at")
    }
    await kafka_producer.send_event("order-events", event_data, key=order_data.get("id"))


