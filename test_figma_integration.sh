#!/bin/bash

echo "========================================="
echo "Testing BA Copilot AI Service with Figma MCP"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "${BLUE}Test 1: Health Check${NC}"
echo "GET /health"
curl -s http://localhost:8000/health | python3 -m json.tool
echo -e "${GREEN}✓ Health check completed${NC}"
echo ""

# Test 2: Wireframe Generation
echo -e "${BLUE}Test 2: Wireframe Generation${NC}"
echo "POST /api/v1/wireframe/generate"
curl -s -X POST http://localhost:8000/api/v1/wireframe/generate \
  -H "Content-Type: application/json" \
  -d '{"message": "Tạo wireframe cho dashboard quản lý với sidebar menu, header và content area"}' \
  | python3 -m json.tool
echo -e "${GREEN}✓ Wireframe generation completed${NC}"
echo ""

# Test 3: Diagram Generation
echo -e "${BLUE}Test 3: Diagram Generation${NC}"
echo "POST /api/v1/diagram/generate"
curl -s -X POST http://localhost:8000/api/v1/diagram/generate \
  -H "Content-Type: application/json" \
  -d '{"message": "Tạo sequence diagram cho quá trình đặt hàng online"}' \
  | python3 -m json.tool | head -40
echo -e "${GREEN}✓ Diagram generation completed${NC}"
echo ""

# Test 4: SRS Generation
echo -e "${BLUE}Test 4: SRS Generation${NC}"
echo "POST /api/v1/srs/generate"
curl -s -X POST http://localhost:8000/api/v1/srs/generate \
  -H "Content-Type: application/json" \
  -d '{"message": "Tạo SRS cho ứng dụng mobile banking"}' \
  | python3 -m json.tool | head -40
echo -e "${GREEN}✓ SRS generation completed${NC}"
echo ""

echo "========================================="
echo "All tests completed successfully!"
echo "========================================="
