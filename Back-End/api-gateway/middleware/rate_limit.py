from fastapi import HTTPException, Request
import redis.asyncio as redis
from typing import Optional
from config import settings


class RateLimiter:
    def __init__(self, redis_client: Optional[redis.Redis]):
        self.redis_client = redis_client
        self.rate_limit = settings.RATE_LIMIT_PER_MINUTE
    
    async def check_rate_limit(self, request: Request):
        """Check rate limit for the request"""
        if not self.redis_client:
            return  # Skip if Redis is not available
        
        # Get client IP
        client_ip = request.client.host
        
        # Create rate limit key
        key = f"rate_limit:{client_ip}"
        
        # Get current count
        current = await self.redis_client.get(key)
        
        if current is None:
            # First request in this window
            await self.redis_client.setex(key, 60, 1)
        elif int(current) >= self.rate_limit:
            # Rate limit exceeded
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {self.rate_limit} requests per minute."
            )
        else:
            # Increment counter
            await self.redis_client.incr(key)
