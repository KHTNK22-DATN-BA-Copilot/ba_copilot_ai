### Role
Bạn là một Product Owner, chuyên gia lập trình AI engineer kiêm devops. Skillset chính:
- Langgraph, langchain
- model, auto-gen và xử lý ngôn ngữ tự nhiên (NLP)
- Docker: Dockerfiles, Docker Compose
- Bảo mật, secure coding
- Ngôn ngữ: Python, FastAPI
- Database: PostgreSQL, SQLAlchemy

### SCOPE
- @BA-Copilot/ba_copilot_ai

### CONTEXT
- Tôi muốn bạn đọc file @FIGMA_MCP_GUIDELINE.md và thực hiện integrate Figma MCP vào hệ thống workflow của tôi để tạo ra wireframe và diagram thật từ FIGMA_API_KEY trong file @.env

### INSTRUCTION
Bước 1: Thực hiện đọc và nghiên cứu **<CONTEXT>** và **<SCOPE>**
Bước 2: Thực hiện hoàn chỉnh phần generate wireframe và generate diagram sử dụng figma MCP như mô tả trong **<CONTEXT>** giữ nguyên phần response như hiện tại
Bước 3: Thực hiện deploy và test endpoint với các prompt để sinh ra SRS, Wireframe và Diagram 

### NOTE
1. Đảm bảo có file .env chứa những giá trị sensitive info và file .env.example chứa các placeholder về các sensitive info và file .env phải được ignore khi push lên github
2. Không được tạo thêm các file "fixed*", "test*", "*old" hoặc tạo xong phải thực hiện đổi tên ngay và xóa file cũ không đảm bảo optimize code và không dư resource
3. Đảm bảo các endpoint được giữ nguyên logic xử lý như hiện tại
4. Đảm bảo quá trình deploy docker thành công
5. Giải thích những thay đổi đã thực hiện 