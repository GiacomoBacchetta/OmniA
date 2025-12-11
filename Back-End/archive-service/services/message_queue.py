import aio_pika
import json
from typing import Dict
from config import settings


class MessageQueueService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue = None
    
    async def connect(self):
        """Connect to RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            
            # Declare queue
            self.queue = await self.channel.declare_queue(
                settings.EMBEDDING_QUEUE_NAME,
                durable=True
            )
            
            print(f"Connected to RabbitMQ: {settings.EMBEDDING_QUEUE_NAME}")
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
    
    async def publish_to_embedding_queue(self, message: Dict):
        """Publish message to embedding queue"""
        if not self.channel:
            await self.connect()
        
        try:
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=settings.EMBEDDING_QUEUE_NAME
            )
            print(f"Published message to queue: {message['item_id']}")
        except Exception as e:
            print(f"Failed to publish message: {e}")
    
    async def close(self):
        """Close connection"""
        if self.connection:
            await self.connection.close()
