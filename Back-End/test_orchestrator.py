#!/usr/bin/env python3
"""
Test script for OmniA Orchestrator Service
Tests agent registration, query processing, and Ollama integration
"""

import requests
import json
import time
from typing import Dict, Any

# Service URLs
ORCHESTRATOR_URL = "http://localhost:8004"
OLLAMA_URL = "http://localhost:11434"


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def check_service_health(url: str, name: str) -> bool:
    """Check if a service is healthy"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✓ {name} is healthy")
            print(f"  Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"✗ {name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ {name} is not reachable: {str(e)}")
        return False


def check_ollama_models() -> bool:
    """Check what models are available in Ollama"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            if models:
                print(f"✓ Ollama has {len(models)} model(s) installed:")
                for model in models:
                    print(f"  - {model.get('name', 'unknown')}")
                return True
            else:
                print("✗ Ollama has no models installed")
                print("  To install a model, run:")
                print("    docker exec -it omnia-ollama ollama pull llama2")
                return False
        else:
            print(f"✗ Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Ollama is not reachable: {str(e)}")
        return False


def list_registered_agents() -> Dict[str, Any]:
    """List all registered agents"""
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/api/v1/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            agents = data.get("agents", [])
            if agents:
                print(f"✓ Found {len(agents)} registered agent(s):")
                for agent in agents:
                    print(f"  - Field: {agent.get('field')}")
                    print(f"    URL: {agent.get('agent_url')}")
            else:
                print("✗ No agents are registered")
                print("  Agents need to register themselves with the orchestrator")
            return data
        else:
            print(f"✗ Failed to list agents: {response.status_code}")
            return {}
    except Exception as e:
        print(f"✗ Error listing agents: {str(e)}")
        return {}


def register_mock_agent(field: str = "test") -> bool:
    """Register a mock agent for testing"""
    try:
        payload = {
            "field": field,
            "agent_url": "http://mock-agent:8010",
            "capabilities": {"rag": True, "vector_search": True}
        }
        response = requests.post(
            f"{ORCHESTRATOR_URL}/api/v1/agents/register",
            json=payload,
            timeout=5
        )
        if response.status_code == 201:
            print(f"✓ Successfully registered mock '{field}' agent")
            return True
        else:
            print(f"✗ Failed to register agent: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error registering agent: {str(e)}")
        return False


def test_query(query: str, fields: list = None) -> Dict[str, Any]:
    """Send a test query to the orchestrator"""
    try:
        payload = {
            "query": query,
            "fields": fields,
            "max_results": 5
        }
        print(f"Sending query: {query}")
        if fields:
            print(f"Target fields: {fields}")
        
        response = requests.post(
            f"{ORCHESTRATOR_URL}/api/v1/query",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Query processed successfully")
            print(f"  Query ID: {data.get('query_id')}")
            print(f"  Agents consulted: {data.get('agents_consulted', [])}")
            print(f"  Processing time: {data.get('processing_time_ms', 0):.2f} ms")
            print(f"  Response: {data.get('response', '')[:200]}...")
            return data
        else:
            print(f"✗ Query failed with status {response.status_code}")
            print(f"  Error: {response.text}")
            return {}
    except Exception as e:
        print(f"✗ Error sending query: {str(e)}")
        return {}


def test_ollama_directly() -> bool:
    """Test Ollama directly with a simple generation request"""
    try:
        payload = {
            "model": "llama2",
            "prompt": "Say hello in one sentence.",
            "stream": False
        }
        print("Testing Ollama directly with a simple prompt...")
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Ollama responded successfully")
            print(f"  Response: {data.get('response', '')[:200]}")
            return True
        else:
            print(f"✗ Ollama returned status {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error testing Ollama: {str(e)}")
        return False


def main():
    """Run all tests"""
    print_section("OmniA Orchestrator Service Test Suite")
    
    # Test 1: Check service health
    print_section("1. Service Health Checks")
    orchestrator_healthy = check_service_health(ORCHESTRATOR_URL, "Orchestrator")
    if not orchestrator_healthy:
        print("\n⚠ Orchestrator is not healthy. Stopping tests.")
        return
    
    # Test 2: Check Ollama
    print_section("2. Ollama Model Check")
    ollama_ready = check_ollama_models()
    
    # Test 3: Test Ollama directly
    if ollama_ready:
        print_section("3. Direct Ollama Test")
        test_ollama_directly()
    
    # Test 4: List registered agents
    print_section("4. Registered Agents")
    agents_data = list_registered_agents()
    has_agents = len(agents_data.get("agents", [])) > 0
    
    # Test 5: Register mock agent if none exist
    if not has_agents:
        print_section("5. Register Mock Agent for Testing")
        register_mock_agent("test")
        time.sleep(0.5)
        list_registered_agents()
    
    # Test 6: Send a test query
    print_section("6. Test Query Processing")
    test_query("What is the weather like today?")
    
    print_section("Test Suite Complete")
    print("\nSummary:")
    print(f"  - Orchestrator: {'✓' if orchestrator_healthy else '✗'}")
    print(f"  - Ollama Models: {'✓' if ollama_ready else '✗'}")
    print(f"  - Registered Agents: {'✓' if has_agents else '✗'}")
    
    if not ollama_ready:
        print("\n⚠ RECOMMENDATION:")
        print("  Install an Ollama model to enable response synthesis:")
        print("    docker exec -it omnia-ollama ollama pull llama2")
    
    if not has_agents:
        print("\n⚠ RECOMMENDATION:")
        print("  Start field agents and register them with the orchestrator")


if __name__ == "__main__":
    main()
