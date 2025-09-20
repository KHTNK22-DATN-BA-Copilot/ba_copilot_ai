# The smaller the number, the higher the priority (in view of an MVP by the end of October)

## 1. Tự động sinh tài liệu đặc tả yêu cầu phần mềm theo template cố định trước (SRS)

### Purpose and details

"Input: tài liệu .md và các prompt trực tiếp
Output: Các tài liệu đặc tả yêu cầu phần mềm (SRS) ở dạng .md
Cung cấp nơi để tạo sinh ra các tài liệu ban đầu, giúp đẩy nhanh quá trình làm việc của BA
Giao diện chủ yếu giống khi thực hiện trao đổi với ChatGPT (dạng khung chat qua lại) (cần bàn thêm)"

### Flow description

"1. Người dùng cung cấp: Prompt + tài liệu (text-based, cụ thể là .md) 2. Người dùng nhấn Enter 3. Hệ thống kiểm tra các thông tin các đầu vào dựa vào các luồng đã định nghĩa; nếu đủ rồi thì đến bước 4
3.1. Hệ thống đưa ra phản hồi về phía người dùng bổ sung các thông tin còn thiếu/ làm rõ các yêu cầu
3.2 Hệ thống chờ người dùng cung cấp thông tin
3.3 Hệ thống nhận và xử lí, kiểm tra các thông tin cung cấp thêm từ phía người dùng
3.4 Lặp lại từ 3.1 đến 3.4 nếu thông tin chưa thỏa mãn yêu cầu của các flow đã định nghĩa; nếu đủ rồi thì đến bước 4 4. Hệ thống tái cấu trúc (nếu cần) và gửi các thông tin đến các LLM 5. Hệ thống hiển thị thông báo đang xử lí, áp dụng xử lí song song để không bị frozen UI 6. Hệ thống lần lượt nhận các kết quả từ các LLMs 7. Hệ thống tái cấu trúc, tái tổ chức lại các kết quả; chuẩn bị ở định dạng và hiển thị lên màn hình người dùng"

### Input

- "Prompt dạng text
- Tài liệu .md"

### Output

- Tài liệu .md, tải xuống được (in the future may include other document formats)

## 2. Tích hợp công cụ thiết kế

### Purpose and details

- Tự động hóa chuyển đổi các yêu-cầu-chức-năng thành một bản phác thảo wireframe cơ bản.
- Tạo ra một sản phẩm trực quan để BA, Designer và Stakeholder có thể thảo luận và điều chỉnh sớm.
- Giảm thiểu công sức cho Designer, chỉ cần hoàn thiện và tối ưu hóa trải nghiệm người dùng.

### Flow description

Bước 1: Người dùng nhấn vào nút hành động ""Tạo Wireframe từ Yêu cầu"".
Bước 2: Ngươi nhập các chức năng hoặc thêm file chứa chức năng được mô tả chi tiết.
Bước 3: Hệ thống gửi nội dung của các yêu cầu đã chọn đến mô hình AI (LLM).
Bước 4: AI phân tích ngữ nghĩa của các yêu cầu và tạo ra một cấu trúc JSON mô tả các thành phần giao diện (UI components) và bố cục (layout) của chúng trên màn hình.
Bước 5: Backend xử lý.
Bước 6: Hệ thống nhận về một liên kết (URL) trỏ đến Frame vừa được tạo.

### Input

Text được nhập trực tiếp.
File chứa text do người dùng thu thập yêu cầu trước đó.

### Output

Link figma/visibly chứa bản prototype sơ bộ của ứng dụng theo các yêu cầu được mô tả.

## 3. Quản lý hội thoại với AI

### Purpose and details

- Tích hợp chatbot AI để hỗ trợ người dùng trong quá trình xây dựng wireframe, prototype và project plan.
- Lưu lại toàn bộ lịch sử hội thoại giữa người dùng và AI, cho phép truy xuất, tìm kiếm và phân tích sau này
- Đảm bảo dữ liệu hội thoại được bảo mật và chỉ hiển thị với người có thẩm quyền.
- Agent của LangChain tự lưu danh sách hội thoại vào db

### Flow description

Bước 1: Người dùng nhập tin nhắn, nhấn nút gửi

Bước 2: Hệ thống sinh 1 session id cho phiên chat đó, 1 phiên chat bao gồm id và danh sách chat.Trong danh sách chat có các chat, mỗi chat bao gồm nội dung và vai trò (người dùng, AI)

Bước 3: Gửi chat mới cho backend.

Bước 4: Backend kiểm tra session của của chat đó. Nếu chưa có nghĩa là chat mới, lưu session id và chat của user vào db, dùng LLM sinh ra câu trả lời cho người, lưu tiếp câu trả lời của AI vào db và đưa ra UI

Bước 5: Nếu session id đã có nghĩa là chat đã có trước đó, dùng LLM sinh ra câu trả lời, truy vấn lấy ra chat với id và lưu tiếp câu trả lời vào đoạn chat tương ứng, trả câu trả lời của AI ra UI

### Input

Text

### Output

- Câu trả lời (tài liệu, bản wireframe, mockup)
- Danh sách đoạn chat (đoạn chat mới nhất được đưa lên đầu)
