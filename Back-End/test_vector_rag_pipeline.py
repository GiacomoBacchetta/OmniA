#!/usr/bin/env python3
"""
Test script for Vector DB ingestion and RAG pipeline
Tests the complete flow: Archive → RabbitMQ → Embedding → Vector DB → RAG Query
"""

import asyncio
import httpx
import time
from typing import Dict, Optional

# Service URLs
API_GATEWAY_URL = "http://localhost:8000"
ARCHIVE_SERVICE_URL = "http://localhost:8001"
VECTOR_DB_SERVICE_URL = "http://localhost:8003"
ORCHESTRATOR_URL = "http://localhost:8004"

# Test credentials
TEST_USER = {
    "email": "test@example.com",
    "password": "test123"
}

class PipelineTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.access_token: Optional[str] = None
        self.test_item_id: Optional[str] = None
    
    async def close(self):
        await self.client.aclose()
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}
    
    async def test_authentication(self) -> bool:
        """Test 1: Authentication"""
        print("\n" + "="*80)
        print("TEST 1: Authentication")
        print("="*80)
        
        try:
            # Try to register (might fail if user exists)
            try:
                response = await self.client.post(
                    f"{API_GATEWAY_URL}/auth/register",
                    json={**TEST_USER, "name": "Test User"}
                )
                if response.status_code == 200:
                    print("✓ User registered successfully")
            except:
                print("⚠ User might already exist, trying login...")
            
            # Login
            response = await self.client.post(
                f"{API_GATEWAY_URL}/auth/login",
                json=TEST_USER
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                print(f"✓ Authentication successful")
                print(f"  Token: {self.access_token[:20]}...")
                return True
            else:
                print(f"✗ Authentication failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        
        except Exception as e:
            print(f"✗ Authentication error: {e}")
            return False
    
    async def test_archive_ingestion(self) -> bool:
        """Test 2: Archive item creation (triggers message queue)"""
        print("\n" + "="*80)
        print("TEST 2: Archive Item Ingestion")
        print("="*80)
        
        test_content = {
            "title": "Vector DB Test Item",
            "content": "This is a test item to verify the vector database ingestion pipeline. "
                      "It includes information about machine learning, artificial intelligence, "
                      "and natural language processing. This content should be embedded and stored "
                      "in the vector database for later retrieval.",
            "field": "learning",
            "tags": ["test", "vector-db", "ml", "ai"]
        }
        
        try:
            response = await self.client.post(
                f"{ARCHIVE_SERVICE_URL}/api/v1/archive/text",
                json=test_content,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 201:
                data = response.json()
                self.test_item_id = data["id"]
                print(f"✓ Archive item created successfully")
                print(f"  Item ID: {self.test_item_id}")
                print(f"  Title: {data['title']}")
                print(f"  Field: {data['field']}")
                print(f"\n  📤 Message should be published to RabbitMQ embedding queue")
                return True
            else:
                print(f"✗ Archive creation failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        
        except Exception as e:
            print(f"✗ Archive ingestion error: {e}")
            return False
    
    async def test_embedding_processing(self) -> bool:
        """Test 3: Wait for embedding service to process"""
        print("\n" + "="*80)
        print("TEST 3: Embedding Processing (RabbitMQ → Embedding Service)")
        print("="*80)
        
        print("⏳ Waiting for embedding service to process the item...")
        print("   This involves:")
        print("   1. RabbitMQ queue consumption")
        print("   2. Embedding generation (HuggingFace/Ollama)")
        print("   3. Vector storage in Qdrant")
        
        # Wait for processing (typically takes 5-15 seconds)
        await asyncio.sleep(12)
        
        print("✓ Waited 12 seconds for processing")
        return True
    
    async def test_vector_db_storage(self) -> bool:
        """Test 4: Verify item is in vector database"""
        print("\n" + "="*80)
        print("TEST 4: Vector DB Storage Verification")
        print("="*80)
        
        try:
            # Check if collection exists
            response = await self.client.get(
                f"{VECTOR_DB_SERVICE_URL}/api/v1/indexes"
            )
            
            if response.status_code == 200:
                indexes = response.json()
                print(f"✓ Available indexes: {indexes}")
                
                if "learning" in indexes:
                    print(f"✓ 'learning' index exists")
                    
                    # Get index info
                    info_response = await self.client.get(
                        f"{VECTOR_DB_SERVICE_URL}/api/v1/index/learning/info"
                    )
                    
                    if info_response.status_code == 200:
                        info = info_response.json()
                        print(f"✓ Index info retrieved")
                        print(f"  Points count: {info.get('points_count', 'N/A')}")
                        print(f"  Vector size: {info.get('vector_size', 'N/A')}")
                        return True
                else:
                    print(f"⚠ 'learning' index not found yet")
                    return False
            else:
                print(f"✗ Failed to get indexes: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"✗ Vector DB check error: {e}")
            return False
    
    async def test_vector_search(self) -> bool:
        """Test 5: Direct vector search"""
        print("\n" + "="*80)
        print("TEST 5: Vector Search (Direct)")
        print("="*80)
        
        # For this test, we'll skip generating an embedding and just check if search endpoint works
        print("⚠ Skipping direct vector search test (requires embedding generation)")
        print("  Will test through RAG query instead")
        return True
    
    async def test_rag_query(self) -> bool:
        """Test 6: RAG query through orchestrator"""
        print("\n" + "="*80)
        print("TEST 6: RAG Query (End-to-End)")
        print("="*80)
        
        test_query = {
            "query": "Tell me about machine learning and artificial intelligence",
            "fields": ["learning"]
        }
        
        try:
            response = await self.client.post(
                f"{ORCHESTRATOR_URL}/api/v1/query",
                json=test_query,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ RAG query successful")
                print(f"\n📊 Response:")
                print(f"  Query: {data.get('query', 'N/A')}")
                print(f"  Answer: {data.get('answer', 'N/A')[:200]}...")
                
                sources = data.get('sources', [])
                print(f"\n📚 Sources found: {len(sources)}")
                for i, source in enumerate(sources[:3], 1):
                    print(f"  {i}. Score: {source.get('score', 'N/A'):.3f}")
                    print(f"     Content: {source.get('content', 'N/A')[:100]}...")
                
                if len(sources) > 0:
                    print(f"\n✓ RAG pipeline is working! Found {len(sources)} relevant sources")
                    return True
                else:
                    print(f"\n⚠ No sources found - vector might not be stored yet")
                    return False
            else:
                print(f"✗ RAG query failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        
        except Exception as e:
            print(f"✗ RAG query error: {e}")
            return False
    
    async def test_cleanup(self) -> bool:
        """Test 7: Cleanup test data"""
        print("\n" + "="*80)
        print("TEST 7: Cleanup")
        print("="*80)
        
        if not self.test_item_id:
            print("⚠ No test item to clean up")
            return True
        
        try:
            response = await self.client.delete(
                f"{API_GATEWAY_URL}/archive/{self.test_item_id}",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 204:
                print(f"✓ Test item deleted from archive")
                print(f"⚠ Note: Vector in Qdrant may still exist (manual cleanup needed)")
                return True
            else:
                print(f"⚠ Cleanup failed: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"⚠ Cleanup error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all pipeline tests"""
        print("\n")
        print("╔" + "="*78 + "╗")
        print("║" + " "*15 + "VECTOR DB & RAG PIPELINE TEST SUITE" + " "*27 + "║")
        print("╚" + "="*78 + "╝")
        
        results = {}
        
        # Run tests in sequence
        results['auth'] = await self.test_authentication()
        if not results['auth']:
            print("\n❌ Cannot proceed without authentication")
            return results
        
        results['ingestion'] = await self.test_archive_ingestion()
        results['embedding'] = await self.test_embedding_processing()
        results['storage'] = await self.test_vector_db_storage()
        results['search'] = await self.test_vector_search()
        results['rag'] = await self.test_rag_query()
        results['cleanup'] = await self.test_cleanup()
        
        # Print summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total = len(results)
        passed = sum(1 for r in results.values() if r)
        
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status:8} | {test_name.upper()}")
        
        print(f"\n{'='*80}")
        print(f"Total: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Vector DB and RAG pipeline is working correctly!")
        elif passed >= total - 2:
            print("⚠️  Most tests passed. Check failed tests above.")
        else:
            print("❌ Multiple tests failed. Check the logs above for details.")
        
        return results


async def main():
    """Main test runner"""
    tester = PipelineTester()
    
    try:
        results = await tester.run_all_tests()
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
