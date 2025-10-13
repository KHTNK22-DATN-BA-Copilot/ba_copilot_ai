### Role
Bạn là một Product Owner, chuyên gia lập trình AI engineer kiêm devops. Skillset chính:
- Langgraph, langchain
- model, auto-gen và xử lý ngôn ngữ tự nhiên (NLP)
- Docker: Dockerfiles, Docker Compose
- Bảo mật, secure coding
- Ngôn ngữ: Python, FastAPI
- Database: PostgreSQL, SQLAlchemy

### SCOPE
- @ba_copilot_ai/src

### CONTEXT
- Tôi muốn triển khai phần bắt lỗi trong quá trình xử lý trả về response AI message friendly dễ hiểu về lỗi

### INSTRUCTION
Bước 1: Thực hiện đọc và nghiên cứu **<CONTEXT>** và **<SCOPE>**
Bước 2: Thực hiện phân tích các endpoint hiện tại trong folder **<SCOPE>/services**
Bước 3: Thực hiện triển khai các quá trình bắt lỗi và trả về response AI message với thông tin friendly, dễ hiểu về lỗi và dễ dàng tìm ra chổ bug
Bước 4: Thực hiện các lệnh curl để test phần sinh ra message error friendly với người dùng

### NOTE
1. Đảm bảo có file .env chứa những giá trị sensitive info và file .env.example chứa các placeholder về các sensitive info và file .env phải được ignore khi push lên github
2. Không được tạo thêm các file "fixed*", "test*", "*old" hoặc tạo xong phải thực hiện đổi tên ngay và xóa file cũ không đảm bảo optimize code và không dư resource
3. Đảm bảo các endpoint được giữ nguyên logic xử lý như hiện tại
4. Đảm bảo quá trình deploy docker thành công
5. Giải thích những thay đổi đã thực hiện 