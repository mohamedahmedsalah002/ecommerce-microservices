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
                "service": "product-service",
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

# Event types for product service
class ProductEvents:
    PRODUCT_CREATED = "product.created"
    PRODUCT_UPDATED = "product.updated"
    PRODUCT_DELETED = "product.deleted"
    PRODUCT_STOCK_UPDATED = "product.stock_updated"
    CATEGORY_CREATED = "category.created"
    CATEGORY_UPDATED = "category.updated"
    CATEGORY_DELETED = "category.deleted"

# Helper functions for common events
async def publish_product_created_event(product_data: Dict[str, Any]):
    """Publish product created event"""
    event_data = {
        "event_type": ProductEvents.PRODUCT_CREATED,
        "product_id": product_data.get("id"),
        "name": product_data.get("name"),
        "price": product_data.get("price"),
        "category_id": product_data.get("category_id"),
        "stock_quantity": product_data.get("stock_quantity"),
        "timestamp": product_data.get("created_at")
    }
    await kafka_producer.send_event("product-events", event_data, key=product_data.get("id"))

async def publish_product_updated_event(product_data: Dict[str, Any]):
    """Publish product updated event"""
    event_data = {
        "event_type": ProductEvents.PRODUCT_UPDATED,
        "product_id": product_data.get("id"),
        "name": product_data.get("name"),
        "price": product_data.get("price"),
        "category_id": product_data.get("category_id"),
        "stock_quantity": product_data.get("stock_quantity"),
        "timestamp": product_data.get("updated_at")
    }
    await kafka_producer.send_event("product-events", event_data, key=product_data.get("id"))

async def publish_product_stock_updated_event(product_data: Dict[str, Any]):
    """Publish product stock updated event"""
    event_data = {
        "event_type": ProductEvents.PRODUCT_STOCK_UPDATED,
        "product_id": product_data.get("id"),
        "stock_quantity": product_data.get("stock_quantity"),
        "previous_stock": product_data.get("previous_stock"),
        "timestamp": product_data.get("updated_at")
    }
    await kafka_producer.send_event("product-events", event_data, key=product_data.get("id"))

async def publish_category_created_event(category_data: Dict[str, Any]):
    """Publish category created event"""
    event_data = {
        "event_type": ProductEvents.CATEGORY_CREATED,
        "category_id": category_data.get("id"),
        "name": category_data.get("name"),
        "description": category_data.get("description"),
        "timestamp": category_data.get("created_at")
    }
    await kafka_producer.send_event("product-events", event_data, key=category_data.get("id"))

