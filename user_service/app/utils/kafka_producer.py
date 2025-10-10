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
                "service": "user-service",
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

# Event types for user service
class UserEvents:
    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"
    USER_UPDATED = "user.updated"
    USER_DEACTIVATED = "user.deactivated"

# Helper functions for common events
async def publish_user_registered_event(user_data: Dict[str, Any]):
    """Publish user registered event"""
    event_data = {
        "event_type": UserEvents.USER_REGISTERED,
        "user_id": user_data.get("id"),
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "timestamp": user_data.get("created_at")
    }
    await kafka_producer.send_event("user-events", event_data, key=user_data.get("id"))

async def publish_user_login_event(user_data: Dict[str, Any]):
    """Publish user login event"""
    event_data = {
        "event_type": UserEvents.USER_LOGIN,
        "user_id": user_data.get("id"),
        "email": user_data.get("email"),
        "timestamp": user_data.get("login_timestamp")
    }
    await kafka_producer.send_event("user-events", event_data, key=user_data.get("id"))

async def publish_user_updated_event(user_data: Dict[str, Any]):
    """Publish user updated event"""
    event_data = {
        "event_type": UserEvents.USER_UPDATED,
        "user_id": user_data.get("id"),
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "timestamp": user_data.get("updated_at")
    }
    await kafka_producer.send_event("user-events", event_data, key=user_data.get("id"))

