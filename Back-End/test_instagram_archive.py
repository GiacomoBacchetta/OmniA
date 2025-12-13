#!/usr/bin/env python3
"""
Test script for Instagram archive item creation
Tests the /api/v1/archive/instagram endpoint
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # API Gateway
INSTAGRAM_ENDPOINT = f"{BASE_URL}/archive/instagram"

def test_create_instagram_archive():
    """Test creating an Instagram archive item"""
    
    print("=" * 60)
    print("Testing Instagram Archive Item Creation")
    print("=" * 60)
    
    # Test data
    test_item = {
        "field": "personal",
        "title": "Beautiful Sunset in Santorini",
        "instagram_url": "https://www.instagram.com/p/test123",
        "tags": ["travel", "sunset", "greece", "photography"],
        "location": {
            "address": "Santorini, Greece",
            "google_maps_url": "https://www.google.com/maps/place/Santorini",
            "latitude": 36.3932,
            "longitude": 25.4615
        }
    }
    
    print(f"\n📤 Sending POST request to: {INSTAGRAM_ENDPOINT}")
    print(f"📋 Request payload:")
    print(json.dumps(test_item, indent=2))
    print()
    
    try:
        # Make the request
        response = requests.post(
            INSTAGRAM_ENDPOINT,
            json=test_item,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
        print()
        
        # Parse response
        if response.status_code == 201:
            data = response.json()
            print("✅ SUCCESS - Instagram item created!")
            print(f"\n📄 Response data:")
            print(json.dumps(data, indent=2))
            
            # Validate response fields
            print("\n🔍 Validation:")
            required_fields = ["id", "field", "content_type", "title", "created_at"]
            for field in required_fields:
                if field in data:
                    print(f"  ✅ {field}: {data[field]}")
                else:
                    print(f"  ❌ {field}: MISSING")
            
            # Check location data
            if data.get("location"):
                print(f"  ✅ location: {data['location']}")
            else:
                print(f"  ⚠️  location: Not present")
            
            return True
            
        elif response.status_code == 503:
            print("❌ FAILED - Service unavailable")
            print("Note: Instagram service might not be configured or might be mocked")
            print(f"\n📄 Error response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
            return False
            
        else:
            print(f"❌ FAILED - Unexpected status code: {response.status_code}")
            print(f"\n📄 Response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR - Could not connect to the server")
        print(f"   Make sure the service is running at {BASE_URL}")
        return False
    except requests.exceptions.Timeout:
        print("❌ ERROR - Request timed out")
        return False
    except Exception as e:
        print(f"❌ ERROR - {type(e).__name__}: {str(e)}")
        return False


def test_verify_item_in_list():
    """Verify the created item appears in the archive list"""
    
    print("\n" + "=" * 60)
    print("Testing Item Retrieval from Archive List")
    print("=" * 60)
    
    list_endpoint = f"{BASE_URL}/archive/items?field=personal"
    
    print(f"\n📤 Sending GET request to: {list_endpoint}")
    
    try:
        response = requests.get(list_endpoint, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            total = data.get("total", 0)
            
            print(f"✅ Retrieved {total} items from 'personal' field")
            
            # Look for Instagram items
            instagram_items = [item for item in items if item.get("content_type") == "instagram"]
            
            if instagram_items:
                print(f"\n✅ Found {len(instagram_items)} Instagram item(s):")
                for item in instagram_items:
                    print(f"  - {item.get('title')} (ID: {item.get('id')[:8]}...)")
            else:
                print("\n⚠️  No Instagram items found in the list")
            
            return len(instagram_items) > 0
        else:
            print(f"❌ Failed to retrieve items: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR - {type(e).__name__}: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n🚀 Starting Instagram Archive Tests")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Test 1: Create Instagram item
    test1_passed = test_create_instagram_archive()
    
    # Test 2: Verify in list (only if creation succeeded)
    test2_passed = False
    if test1_passed:
        test2_passed = test_verify_item_in_list()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Create Instagram Item: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Verify in List:        {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print()
    
    if test1_passed and test2_passed:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
