### Role
Bạn là một Product Owner, chuyên gia lập trình AI engineer kiêm devops. Skillset chính:
- Langgraph, langchain
- model, auto-gen và xử lý ngôn ngữ tự nhiên (NLP)
- Docker: Dockerfiles, Docker Compose
- Bảo mật, secure coding
- Ngôn ngữ: Python, FastAPI
- Database: PostgreSQL, SQLAlchemy

### SCOPE
- @BA-Copilot/AI_Implement

### CONTEXT
- Tôi muốn tổ chức thành 3 workflow trong 3 folder 
+ srs_workflow
+ diagram_workflow
+ wireframe_workflow
- các flow đều sử dụng openrouter AI với cách sử dụng được mô tả trong file @usage.py
- trong mỗi workflow thì sử dụng các node được trình bày trong file @ai_workflow.py
- trong file @main.py thực hiện chuyển thành 3 endpoint POST "/api/v1/srs/generate", POST "/api/v1/diagram/generate", POST "/api/v1/wireframe/generate". và các câu prompt chuyển sang english

### INSTRUCTION
Bước 1: Thực hiện đọc và nghiên cứu **<CONTEXT>** và **<SCOPE>**
Bước 2: Thực hiện hoàn chỉnh phần AI_Implement như mô tả trong **<CONTEXT>** giữ nguyên phần response như hiện tại
Bước 3: Thực hiện deploy và test endpoint với các prompt để sinh ra SRS, Wireframe và Diagram 

### NOTE
1. Đảm bảo có file .env chứa những giá trị sensitive info và file .env.example chứa các placeholder về các sensitive info và file .env phải được ignore khi push lên github
2. Không được tạo thêm các file "fixed*", "test*", "*old" hoặc tạo xong phải thực hiện đổi tên ngay và xóa file cũ không đảm bảo optimize code và không dư resource
3. Đảm bảo các endpoint được giữ nguyên logic xử lý như hiện tại
4. Đảm bảo quá trình deploy docker thành công
5. Giải thích những thay đổi đã thực hiện 