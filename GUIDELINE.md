# Hướng Dẫn Triển Khai và Sử Dụng API - BA Copilot AI

Tài liệu này cung cấp hướng dẫn chi tiết về cách triển khai môi trường development và cách sử dụng các API endpoint của dự án BA Copilot AI.

## 1. Tổng Quan

BA Copilot AI là một hệ thống backend cung cấp các dịch vụ AI để hỗ trợ các nhà phân tích nghiệp vụ (Business Analysts). Các dịch vụ chính bao gồm:

- **Health Check**: Kiểm tra trạng thái hoạt động của hệ thống.
- **SRS (Software Requirements Specification) Generator**: Tạo tài liệu đặc tả yêu cầu phần mềm.
- **Diagram Generator**: Tạo các loại biểu đồ (sequence, architecture, flowchart).
- **Wireframe Generator**: Tạo wireframe cho giao diện người dùng.
- **AI Conversations**: Quản lý các cuộc hội thoại với AI.

## 2. Hướng Dẫn Triển Khai (Development)

### Yêu Cầu

- Docker
- Docker Compose

### Các Bước Triển Khai

1.  **Tạo file môi trường `.env`**:

    Tạo một file có tên `.env` ở thư mục gốc của dự án (`ba_copilot_ai`) và sao chép nội dung dưới đây vào. File này chứa các biến môi trường cần thiết để các container có thể giao tiếp với nhau.

    ```dotenv
    # Application Environment
    ENVIRONMENT=development
    DEBUG=true
    LOG_LEVEL=DEBUG
    PYTHONPATH=/app/src

    # PostgreSQL Database
    # Lưu ý: Tên host 'ba-copilot-postgres' là tên service trong docker-compose.yml
    DATABASE_URL=postgresql://bacopilot_user:dev_password@ba-copilot-postgres:5432/bacopilot
    POSTGRES_DB=bacopilot
    POSTGRES_USER=bacopilot_user
    POSTGRES_PASSWORD=dev_password

    # Redis Cache
    # Lưu ý: Tên host 'ba-copilot-redis' là tên service trong docker-compose.yml
    REDIS_URL=redis://ba-copilot-redis:6379/0

    # AI Providers API Keys (thay bằng key của bạn nếu có)
    GOOGLE_AI_API_KEY="YOUR_GOOGLE_AI_API_KEY"
    CLAUDE_API_KEY="YOUR_CLAUDE_API_KEY"
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

    # JWT Secret Key (sẽ dùng cho xác thực)
    SECRET_KEY="your-super-secret-key-for-jwt"
    ```

2.  **Chạy Docker Compose**:

    Mở terminal tại thư mục gốc của dự án và chạy lệnh sau để khởi tạo và chạy tất cả các service (API, database, Redis):

    ```bash
    docker-compose -f infrastructure/docker-compose.yml up --build -d
    ```

3.  **Kiểm tra trạng thái**:

    Sau khi các container đã khởi động (có thể mất vài phút), bạn có thể kiểm tra trạng thái của chúng:

    ```bash
    docker-compose -f infrastructure/docker-compose.yml ps
    ```

    Bạn sẽ thấy các service `ba-copilot-ai-app`, `ba-copilot-postgres`, `ba-copilot-redis` đang ở trạng thái `running` hoặc `healthy`.

4.  **Truy cập API**:

    - **API Base URL**: `http://localhost:8000`
    - **API Documentation (Swagger UI)**: `http://localhost:8000/docs`
    - **Health Check**: `http://localhost:8000/v1/health/`

## 3. Danh Sách API Endpoints và Cách Sử Dụng

Dưới đây là danh sách các endpoint và cách kiểm tra chúng bằng `curl`.

---

### 3.1. Health Service

Endpoint để kiểm tra "sức khỏe" của hệ thống.

#### **GET /v1/health/**

- **Mô tả**: Lấy trạng thái chi tiết của dịch vụ, bao gồm các dịch vụ phụ thuộc.
- **Lệnh `curl`**:
  ```bash
  curl -X GET "http://localhost:8000/v1/health/"
  ```
- **Phản hồi mẫu (200 OK)**:
  ```json
  {
    "status": "healthy",
    "timestamp": "2023-10-27T10:00:00.123456Z",
    "version": "1.0.0",
    "environment": "development",
    "services": {
      "database": "healthy",
      "llm_providers": "healthy",
      "file_storage": "healthy",
      "cache": "healthy"
    },
    "uptime_seconds": 86400
  }
  ```

#### **GET /v1/health/ping**

- **Mô tả**: Một endpoint đơn giản để kiểm tra dịch vụ có phản hồi hay không.
- **Lệnh `curl`**:
  ```bash
  curl -X GET "http://localhost:8000/v1/health/ping"
  ```
- **Phản hồi mẫu (200 OK)**:
  ```json
  {
    "message": "pong"
  }
  ```

---

### 3.2. SRS Service

Endpoint để tạo và quản lý tài liệu SRS.

#### **POST /v1/srs/generate**

- **Mô tả**: Tạo một tài liệu SRS mới từ mô tả dự án.
- **Lệnh `curl`**:
  ```bash
  curl -X POST "http://localhost:8000/v1/srs/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "project_input": "Create a web-based math learning game for elementary students"
  }'
  ```
- **Phản hồi mẫu (200 OK)**:
  ```json
  {
    "document_id": "doc_...",
    "generated_at": "...",
    "input_description": "Create a web-based math learning game for elementary students",
    "document": {
      "title": "...",
      "content": "..."
    },
    "status": "completed"
  }
  ```

#### **GET /v1/srs/{document_id}**

- **Mô tả**: Lấy thông tin một tài liệu SRS đã được tạo.
- **Lệnh `curl`** (thay `doc_123` bằng ID hợp lệ):
  ```bash
  curl -X GET "http://localhost:8000/v1/srs/doc_123"
  ```
- **Phản hồi mẫu (200 OK)**:
  ```json
  {
    "document_id": "doc_123",
    "project_name": "E-commerce Platform",
    "content": "# Software Requirements Specification...",
    "metadata": { ... }
  }
  ```

#### **GET /v1/srs/{document_id}/export**

- **Mô tả**: Lấy thông tin để tải về tài liệu SRS theo định dạng.
- **Lệnh `curl`** (thay `doc_123` bằng ID hợp lệ):
  ```bash
  curl -X GET "http://localhost:8000/v1/srs/doc_123/export?format=pdf"
  ```
- **Phản hồi mẫu (200 OK)**:
  ```json
  {
    "download_url": "http://localhost:8000/exports/doc_123.pdf",
    "expires_at": "2025-09-21T14:30:00Z",
    "file_size_bytes": 245760,
    "format": "pdf"
  }
  ```

---

### 3.3. Diagram Service

Endpoint để quản lý và xuất các biểu đồ.

#### **GET /v1/diagrams/**

- **Mô tả**: Liệt kê danh sách các biểu đồ đã tạo.
- **Lệnh `curl`**:
  ```bash
  curl -X GET "http://localhost:8000/v1/diagrams/"
  ```
- **Phản hồi mẫu (200 OK)**:
  ```json
  {
    "diagrams": [ ... ],
    "total_count": 4,
    "has_next": false
  }
  ```

#### **GET /v1/diagrams/{diagram_id}**

- **Mô tả**: Lấy thông tin chi tiết của một biểu đồ.
- **Lệnh `curl`** (thay `diag_123` bằng ID hợp lệ):
  ```bash
  curl -X GET "http://localhost:8000/v1/diagrams/diag_123"
  ```
- **Phản hồi mẫu (200 OK)**:
  ```json
  {
    "diagram_id": "diag_123",
    "type": "sequence",
    "title": "User Authentication Flow",
    "mermaid_code": "sequenceDiagram...",
    "preview_url": "http://localhost:8000/v1/diagrams/diag_123/preview",
    "metadata": { ... }
  }
  ```

#### **GET /v1/diagrams/{diagram_id}/export**

- **Mô tả**: Lấy thông tin để tải về biểu đồ theo định dạng.
- **Lệnh `curl`** (thay `diag_123` bằng ID hợp lệ):
  ```bash
  curl -X GET "http://localhost:8000/v1/diagrams/diag_123/export?format=svg&theme=dark"
  ```
- **Phản hồi mẫu (200 OK)**:
  ```json
  {
    "download_url": "http://localhost:8000/exports/diag_123.svg",
    "expires_at": "2025-09-21T14:30:00Z",
    "file_size_bytes": 12288,
    "format": "svg",
    "quality": "medium",
    "theme": "dark"
  }
  ```

---

### 3.4. Wireframe Service

Endpoint để quản lý wireframe.

#### **GET /v1/wireframes/{wireframe_id}**

- **Mô tả**: Lấy thông tin chi tiết của một wireframe.
- **Lệnh `curl`** (thay `wf_123` bằng ID hợp lệ):
  ```bash
  curl -X GET "http://localhost:8000/v1/wireframes/wf_123"
  ```
- **Phản hồi mẫu (200 OK)**:
  ```json
  {
    "wireframe_id": "wf_123",
    "preview_url": "http://localhost:8000/v1/wireframes/wf_123/preview",
    "html_content": "<!DOCTYPE html>...",
    "css_styles": "/* Generated CSS styles */...",
    "components_identified": [ ... ],
    "metadata": { ... }
  }
  ```

#### **GET /v1/wireframes/{wireframe_id}/export**

- **Mô tả**: Lấy thông tin để tải về wireframe theo định dạng.
- **Lệnh `curl`** (thay `wf_123` bằng ID hợp lệ):
  ```bash
  curl -X GET "http://localhost:8000/v1/wireframes/wf_123/export?format=zip"
  ```
- **Phản hồi mẫu (200 OK)**:
  ```json
  {
    "download_url": "http://localhost:8000/exports/wf_123.zip",
    "expires_at": "2025-09-21T14:30:00Z",
    "file_size_bytes": 25600,
    "format": "zip"
  }
  ```

---

### 3.5. Conversation Service

Endpoint để quản lý các cuộc hội thoại.

#### **GET /v1/conversations/**

- **Mô tả**: Liệt kê danh sách các cuộc hội thoại.
- **Lệnh `curl`**:
  ```bash
  curl -X GET "http://localhost:8000/v1/conversations/"
  ```
- **Phản hồi mẫu (200 OK)**:
  ```json
  {
    "conversations": [ ... ],
    "total_count": 4,
    "has_next": false
  }
  ```

#### **GET /v1/conversations/{conversation_id}**

- **Mô tả**: Lấy lịch sử và thông tin chi tiết của một cuộc hội thoại.
- **Lệnh `curl`** (thay `conv_123` bằng ID hợp lệ):
  ```bash
  curl -X GET "http://localhost:8000/v1/conversations/conv_123"
  ```
- **Phản hồi mẫu (200 OK)**:
  ```json
  {
    "conversation_id": "conv_123",
    "title": "E-commerce SRS Development Discussion",
    "messages": [ ... ],
    "metadata": { ... },
    "created_at": "2025-09-20T14:30:00Z",
    "updated_at": "2025-09-20T14:32:45Z"
  }
  ```
