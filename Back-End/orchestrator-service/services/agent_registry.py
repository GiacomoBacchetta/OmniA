import json
from typing import Dict, List, Optional
from datetime import datetime
import redis.asyncio as redis
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class AgentRegistry:
    """Manages registration and discovery of field-specific agents"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.agents_key = "agents:registry"
    
    async def register_agent(
        self,
        field: str,
        agent_url: str,
        capabilities: Optional[Dict] = None
    ):
        """Register a new agent"""
        # Ensure agent_url is a string (convert from HttpUrl if needed)
        url_str = str(agent_url) if not isinstance(agent_url, str) else agent_url
        # Remove trailing slash to avoid double slashes in URL construction
        url_str = url_str.rstrip('/')
        
        agent_data = {
            "field": field,
            "agent_url": url_str,
            "capabilities": capabilities or {},
            "registered_at": datetime.utcnow().isoformat()
        }
        
        await self.redis.hset(
            self.agents_key,
            field,
            json.dumps(agent_data)
        )
        print(f"Registered agent for field: {field}")
    
    async def unregister_agent(self, field: str):
        """Unregister an agent"""
        await self.redis.hdel(self.agents_key, field)
        print(f"Unregistered agent for field: {field}")
    
    async def get_agent(self, field: str) -> Dict:
        """Get agent information for a specific field"""
        data = await self.redis.hget(self.agents_key, field)
        if not data:
            raise Exception(f"No agent registered for field: {field}")
        return json.loads(data)
    
    async def list_agents(self) -> List[Dict]:
        """List all registered agents"""
        agents_data = await self.redis.hgetall(self.agents_key)
        logger.info(f"Listing all registered agents: {list(agents_data.keys())}")
        return [json.loads(data) for data in agents_data.values()]
    
    async def get_agents_for_fields(self, fields: List[str]) -> Dict[str, Dict]:
        """Get agents for multiple fields"""
        agents = {}
        for field in fields:
            try:
                agents[field] = await self.get_agent(field)
            except Exception:
                print(f"No agent found for field: {field}")
        return agents
