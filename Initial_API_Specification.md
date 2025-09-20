# API_Specification

## 1. Tổng quan
Tài liệu liệt kê các endpoint cho frontend kết nối backend (FastAPI) đảm bảo các tính năng: Auth, SRS Generator, Wireframe Generator, AI Conversations, Diagrams.

## 2. Cấu trúc chung
- **Base URL:** `https://api.yourdomain.com/v1`
- **Authentication:** JWT Bearer Token
- **Headers chung:**
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`

## 3. Endpoint chi tiết

### 3.1 Authentication

| Endpoint            | Method | URL                 | Description                | Request Body                          | Response                  |
|---------------------|--------|---------------------|----------------------------|---------------------------------------|---------------------------|
| Đăng ký             | POST   | /auth/register      | Tạo tài khoản mới          | `{ "email": "string", "password": "string" }` | `{ "userId": "uuid", "token": "string" }` |
| Đăng nhập           | POST   | /auth/login         | Đăng nhập và lấy token     | `{ "email": "string", "password": "string" }` | `{ "token": "string" }` |

### 3.2 SRS Generator

| Endpoint            | Method | URL                 | Description                | Request Body                          | Response                  |
|---------------------|--------|---------------------|----------------------------|---------------------------------------|---------------------------|
| Sinh SRS            | POST   | /srs/generate       | Sinh tài liệu SRS theo template | `{ "projectName": "string", "overview": "string", "features": ["string"] }` | `{ "documentId": "uuid", "content": "markdown|string" }` |
| Lấy SRS             | GET    | /srs/{documentId}   | Lấy nội dung SRS đã sinh    | -                                     | `{ "content": "markdown|string" }` |

### 3.3 Wireframe Generator

| Endpoint            | Method | URL                 | Description                | Request Body                          | Response                  |
|---------------------|--------|---------------------|----------------------------|---------------------------------------|---------------------------|
| Sinh wireframe      | POST   | /wireframe/generate | Sinh wireframe từ mô tả text | `{ "pageDescription": "string", "template": "string" }` | `{ "wireframeId": "uuid", "html": "string" }` |
| Lấy wireframe       | GET    | /wireframe/{id}     | Lấy wireframe đã sinh      | -                                     | `{ "html": "string" }` |

### 3.4 AI Conversations

| Endpoint                 | Method | URL                     | Description                  | Request Body                                         | Response                          |
|--------------------------|--------|-------------------------|------------------------------|------------------------------------------------------|-----------------------------------|
| Tạo conversation mới     | POST   | /conversations          | Bắt đầu hội thoại mới        | `{ "title": "string" }`                          | `{ "conversationId": "uuid" }` |
| Gửi tin nhắn             | POST   | /conversations/{id}/send| Gửi tin nhắn tới AI          | `{ "message": "string" }`                        | `{ "reply": "string" }`       |
| Lấy lịch sử hội thoại     | GET    | /conversations/{id}     | Lấy toàn bộ tin nhắn         | -                                                    | `{ "messages": [{"from":"user|ai","text":"string","timestamp":"iso"}] }` |

### 3.5 Diagrams (Optional)

| Endpoint                   | Method | URL                       | Description                   | Request Body                                           | Response                           |
|----------------------------|--------|---------------------------|-------------------------------|--------------------------------------------------------|------------------------------------|
| Sinh diagram               | POST   | /diagrams/generate        | Sinh diagram theo mô tả       | `{ "type": "sequence|usecase|class", "description": "string" }` | `{ "diagramId": "uuid", "svg": "string" }` |
| Lấy diagram                | GET    | /diagrams/{id}            | Lấy diagram đã sinh           | -                                                      | `{ "svg": "string" }`          |

### 3.6 User Profile / Settings

| Endpoint                    | Method | URL                     | Description                   | Request Body                          | Response                          |
|-----------------------------|--------|-------------------------|-------------------------------|---------------------------------------|-----------------------------------|
| Lấy thông tin người dùng     | GET    | /users/me               | Lấy profile hiện tại          | -                                     | `{ "userId":"uuid","email":"string" }` |
| Cập nhật thông tin người dùng | PUT    | /users/me               | Cập nhật profile              | `{ "email": "string", "settings": { } }` | `{ "success": true }`           |

## 4. Error Handling
- Trả về JSON `{ "detail": "error message" }` cùng HTTP status code phù hợp (400,401,404,500...).