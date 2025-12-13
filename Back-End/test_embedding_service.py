#!/usr/bin/env python3
"""Test script for the embedding service via RabbitMQ"""

import asyncio
import json
import sys

try:
    import aio_pika
except ImportError:
    print("Installing aio-pika...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aio-pika"])
    import aio_pika


async def test_embedding_service():
    """Send a test message to the embedding service queue"""
    try:
        # Connect to RabbitMQ
        print("Connecting to RabbitMQ...")
        connection = await aio_pika.connect_robust('amqp://guest:guest@localhost:5672/')
        
        async with connection:
            channel = await connection.channel()
            
            # Create test message
            message_data = {
                'item_id': 'test_embedding_001',
                'field': 'test_content',
                'content': 'This is a test message to generate embeddings using the embedding service',
                'content_type': 'text',
                'metadata': {
                    'source': 'test_script',
                    'timestamp': '2025-12-12T12:00:00Z'
                }
            }
            
            print(f"\nSending test message:")
            print(f"  Item ID: {message_data['item_id']}")
            print(f"  Content: {message_data['content']}")
            
            # Publish message to embedding queue
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message_data).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key='embedding_queue'
            )
            
            print("\n✓ Test message sent successfully to embedding_queue!")
            print("\nCheck the embedding service logs with:")
            print("  docker logs omnia-embedding-service -f")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_embedding_service())
    sys.exit(0 if success else 1)
