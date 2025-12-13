#!/usr/bin/env python3
"""
Quick test to verify embedding was stored and can be retrieved from Qdrant
"""

import asyncio
import httpx

async def test_direct_qdrant():
    """Test direct Qdrant access"""
    async with httpx.AsyncClient() as client:
        # Check collection info
        print("Checking Qdrant collection 'learning'...")
        response = await client.get("http://localhost:6333/collections/learning")
        data = response.json()
        
        print(f"✓ Collection status: {data['result']['status']}")
        print(f"✓ Points count: {data['result']['points_count']}")
        print(f"✓ Vector size: {data['result']['config']['params']['vectors']['size']}")
        print(f"✓ Distance: {data['result']['config']['params']['vectors']['distance']}")
        
        # Scroll through points to see what's stored
        print("\nFetching stored points...")
        scroll_response = await client.post(
            "http://localhost:6333/collections/learning/points/scroll",
            json={"limit": 5, "with_payload": True, "with_vector": False}
        )
        scroll_data = scroll_response.json()
        
        points = scroll_data['result']['points']
        print(f"\nFound {len(points)} points:")
        for i, point in enumerate(points, 1):
            print(f"\n{i}. Point ID: {point['id']}")
            payload = point.get('payload', {})
            print(f"   Title: {payload.get('title', 'N/A')}")
            print(f"   Content: {payload.get('content', 'N/A')[:100]}...")
            print(f"   Field: {payload.get('field', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(test_direct_qdrant())
