import asyncio
import json
import aio_pika
from typing import Dict
from config import settings
from services.embedding_generator import EmbeddingGenerator
from services.vector_store import VectorStoreService

# Initialize services
embedding_generator = EmbeddingGenerator()
vector_store = VectorStoreService()


async def process_message(message: aio_pika.IncomingMessage):
    """Process a message from the queue"""
    async with message.process():
        try:
            # Parse message
            data = json.loads(message.body.decode())
            
            print(f"Processing item: {data['item_id']}")
            
            # Generate embedding
            embedding = await embedding_generator.generate_embedding(
                data['content'],
                data.get('content_type', 'text')
            )
            
            # Store in vector database
            await vector_store.store_embedding(
                item_id=data['item_id'],
                field=data['field'],
                embedding=embedding,
                content=data['content'],
                metadata=data.get('metadata', {})
            )
            
            print(f"Successfully processed item: {data['item_id']}")
        
        except Exception as e:
            print(f"Error processing message: {e}")
            # In production, implement dead letter queue


async def main():
    """Main consumer loop"""
    print(f"Starting Embedding Service...")
    print(f"Connecting to RabbitMQ: {settings.RABBITMQ_URL}")
    
    # Connect to RabbitMQ
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=settings.MAX_WORKERS)
        
        # Declare queue
        queue = await channel.declare_queue(
            settings.EMBEDDING_QUEUE_NAME,
            durable=True
        )
        
        print(f"Waiting for messages on queue: {settings.EMBEDDING_QUEUE_NAME}")
        
        # Start consuming
        await queue.consume(process_message)
        
        # Wait forever
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
