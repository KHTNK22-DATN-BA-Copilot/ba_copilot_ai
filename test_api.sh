#!/bin/bash

# Test script for BA Copilot AI Service
BASE_URL="http://localhost:8000"

echo "=========================================="
echo "BA Copilot AI Service - API Tests"
echo "=========================================="

# Test 1: Root endpoint
echo -e "\n1. Testing root endpoint..."
curl -s "$BASE_URL/" | jq .

# Test 2: Health check
echo -e "\n2. Testing health check..."
curl -s "$BASE_URL/health" | jq .

# Test 3: Generate SRS
echo -e "\n3. Testing SRS generation..."
curl -s -X POST "$BASE_URL/ai/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tạo SRS cho hệ thống quản lý thư viện với các chức năng: quản lý sách, mượn trả sách, quản lý thành viên"
  }' | jq .

# Test 4: Generate Wireframe
echo -e "\n4. Testing Wireframe generation..."
curl -s -X POST "$BASE_URL/ai/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tạo wireframe cho trang đăng nhập và dashboard admin"
  }' | jq .

# Test 5: Generate Diagram
echo -e "\n5. Testing Diagram generation..."
curl -s -X POST "$BASE_URL/ai/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tạo ERD cho hệ thống quản lý bán hàng với các bảng: Product, Order, Customer, OrderDetail"
  }' | jq .

echo -e "\n=========================================="
echo "All tests completed!"
echo "=========================================="
