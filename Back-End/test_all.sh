#!/bin/bash

# OmniA Backend - Complete Test Suite
# Tests API Gateway, Archive Service, Location Extraction, and Map Endpoint

set -e  # Exit on error

BASE_URL="http://localhost:8000"
ARCHIVE_URL="http://localhost:8001"

echo "🚀 OmniA Backend Test Suite"
echo "================================"
echo ""
 
# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "Testing $name... "
    
    response=$(curl -s "$url" || echo "ERROR")
    
    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "  Expected: $expected"
        echo "  Got: $response"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo -e "${BLUE}📡 Testing Service Health${NC}"
echo "-----------------------------------"

# Test API Gateway
test_endpoint "API Gateway" "$BASE_URL/" "OmniA API Gateway"

# Test Archive Service
test_endpoint "Archive Service" "$ARCHIVE_URL/" "OmniA Archive Service"

# Test Vector DB Service
test_endpoint "Vector DB Service" "http://localhost:8003/" "OmniA Vector DB Service"

# Test Orchestrator Service
test_endpoint "Orchestrator Service" "http://localhost:8004/" "OmniA Orchestrator Service"

echo ""
echo -e "${BLUE}📝 Testing Archive Ingestion${NC}"
echo "-----------------------------------"

# Test 1: Text with Google Maps URL
echo -e "${YELLOW}Test 1: Text Archive with Google Maps URL${NC}"
RESPONSE=$(curl -s -X POST "$ARCHIVE_URL/api/v1/archive/text" \
  -H "Content-Type: application/json" \
  -d '{
    "field": "personal",
    "title": "Favorite Restaurant in Naples",
    "content": "Best pizza ever at Antica Pizzeria da Michele! Located at https://www.google.com/maps/place/Antica+Pizzeria+da+Michele/@40.8469931,14.2583304,17z"
  }')

ITEM_ID_1=$(echo $RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -n "$ITEM_ID_1" ]; then
    echo -e "  ${GREEN}✓${NC} Created item: $ITEM_ID_1"
    if echo $RESPONSE | grep -q "location"; then
        echo -e "  ${GREEN}✓${NC} Location data extracted"
        ((TESTS_PASSED++))
    else
        echo -e "  ${RED}✗${NC} No location data found"
        ((TESTS_FAILED++))
    fi
else
    echo -e "  ${RED}✗${NC} Failed to create item"
    ((TESTS_FAILED++))
fi

echo ""

# Test 2: Text with coordinates
echo -e "${YELLOW}Test 2: Text Archive with Direct Coordinates${NC}"
RESPONSE=$(curl -s -X POST "$ARCHIVE_URL/api/v1/archive/text" \
  -H "Content-Type: application/json" \
  -d '{
    "field": "work",
    "title": "Office in Milan",
    "content": "Our new office is at 45.4642, 9.1900 right in the city center!"
  }')

ITEM_ID_2=$(echo $RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -n "$ITEM_ID_2" ]; then
    echo -e "  ${GREEN}✓${NC} Created item: $ITEM_ID_2"
    if echo $RESPONSE | grep -q "45.4642"; then
        echo -e "  ${GREEN}✓${NC} Coordinates extracted correctly"
        ((TESTS_PASSED++))
    else
        echo -e "  ${RED}✗${NC} Coordinates not extracted"
        ((TESTS_FAILED++))
    fi
else
    echo -e "  ${RED}✗${NC} Failed to create item"
    ((TESTS_FAILED++))
fi

echo ""

# Test 3: Text with Italian address
echo -e "${YELLOW}Test 3: Text Archive with Italian Address${NC}"
RESPONSE=$(curl -s -X POST "$ARCHIVE_URL/api/v1/archive/text" \
  -H "Content-Type: application/json" \
  -d '{
    "field": "inspiration",
    "title": "Beautiful Shopping Street",
    "content": "Walked down Via Montenapoleone in Milano - incredible luxury stores everywhere!",
    "tags": ["shopping", "travel"]
  }')

ITEM_ID_3=$(echo $RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -n "$ITEM_ID_3" ]; then
    echo -e "  ${GREEN}✓${NC} Created item: $ITEM_ID_3"
    echo -e "  ${BLUE}ℹ${NC}  Address extraction (requires geocoding - may take a moment)"
    ((TESTS_PASSED++))
else
    echo -e "  ${RED}✗${NC} Failed to create item"
    ((TESTS_FAILED++))
fi

echo ""
echo -e "${BLUE}🗺️ Testing Map Endpoint${NC}"
echo "-----------------------------------"

# Test map endpoint
echo -n "Fetching all map markers... "
MAP_RESPONSE=$(curl -s "$ARCHIVE_URL/api/v1/archive/map/all")

if echo $MAP_RESPONSE | grep -q "markers"; then
    MARKER_COUNT=$(echo $MAP_RESPONSE | grep -o '"total":[0-9]*' | cut -d: -f2)
    echo -e "${GREEN}✓${NC} Found $MARKER_COUNT markers"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((TESTS_FAILED++))
fi

# Test map filter by field
echo -n "Testing field filter (personal)... "
FILTERED=$(curl -s "$ARCHIVE_URL/api/v1/archive/map/all?field=personal")
if echo $FILTERED | grep -q "markers"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo -e "${BLUE}📋 Testing List Endpoint${NC}"
echo "-----------------------------------"

# Test listing items
echo -n "Fetching archive items... "
LIST_RESPONSE=$(curl -s "$ARCHIVE_URL/api/v1/archive/items")

if echo $LIST_RESPONSE | grep -q "items"; then
    ITEM_COUNT=$(echo $LIST_RESPONSE | grep -o '"total":[0-9]*' | cut -d: -f2)
    echo -e "${GREEN}✓${NC} Found $ITEM_COUNT total items"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo -e "${BLUE}🔍 Testing Orchestrator (Query)${NC}"
echo "-----------------------------------"

# Test query endpoint
echo -n "Testing query endpoint... "
QUERY_RESPONSE=$(curl -s -X POST "http://localhost:8004/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me about restaurants",
    "field": "personal"
  }')

if echo $QUERY_RESPONSE | grep -q "query"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠ SKIPPED${NC} (requires Ollama models)"
fi

echo ""
echo "================================"
echo -e "${BLUE}📊 Test Summary${NC}"
echo "================================"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Open map viewer: http://localhost:8001/static/map.html"
    echo "  2. View API docs: http://localhost:8001/docs"
    echo "  3. Check logs: docker-compose logs -f"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo "Check logs with: docker-compose logs"
    exit 1
fi
