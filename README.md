# 🧠 ThamAI Backend (Flask API)

Đây là **API backend chính thức của Trợ lý ảo ThamAI**, được xây dựng bằng **Flask + OpenAI + Whisper miễn phí (HuggingFace)**.  
Nhiệm vụ của backend là **xử lý hội thoại, nhận diện giọng nói (STT)** và **phát giọng (TTS)** cho frontend hoạt động mượt mà.

---

## ⚙️ Tính năng chính

- 💬 **/chat** – Nhận tin nhắn văn bản, gọi GPT và trả về phản hồi.  
- 🎤 **/speech-to-text** – Nhận file âm thanh `.webm` (ghi từ trình duyệt), gửi lên **Whisper API miễn phí** của HuggingFace để chuyển thành văn bản.  
- 📜 **/logs** – Lấy lịch sử hội thoại.  
- 🗑️ **/logs/clear** – Xóa toàn bộ lịch sử.  
- 🩺 **/healthz** – Kiểm tra tình trạng hoạt động server.  

---

## 📁 Cấu trúc dự án

```plaintext
📁 ThamAI_Backend_clean/
├── app.py               # Flask app chính
├── requirements.txt     # Thư viện cần thiết
├── .env                 # Khóa API OpenAI và HuggingFace
└── README.md            # Tài liệu hướng dẫn này
🧩 File .env mẫu

Tạo file .env trong thư mục dự án và dán nội dung sau:

OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HF_API_URL=https://api-inference.huggingface.co/models/openai/whisper-tiny
HF_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


🔹 Lưu ý:

OPENAI_API_KEY dùng để gọi GPT (phần chat).

HF_API_KEY dùng để gọi Whisper miễn phí qua HuggingFace (phần nhận diện giọng nói).

Khi test nội bộ, API Whisper miễn phí có thể hơi chậm vài giây.

🧠 Cài đặt và chạy thử cục bộ

Mở Terminal trong thư mục ThamAI_Backend_clean

Cài thư viện cần thiết:

pip install -r requirements.txt


Chạy Flask server:

python app.py


Mở trình duyệt tại địa chỉ:

http://127.0.0.1:5000/healthz


Nếu thấy { "status": "ok" } là backend đã hoạt động.

🌐 Triển khai lên Render (đề xuất chính thức)

Đưa toàn bộ dự án lên GitHub (repo: ThamAI_Backend_clean).

Truy cập https://render.com
 → New + Web Service

Kết nối GitHub, chọn repo này.

Cấu hình:

Build Command: pip install -r requirements.txt

Start Command: gunicorn app:app

Environment Variables: copy toàn bộ .env

Nhấn Deploy → Backend sẽ có link dạng:

https://thamai-backend-new.onrender.com/

📡 Kết nối với Frontend

Trong script.js của frontend, thay đúng địa chỉ backend:

const BACKEND_URL = "https://thamai-backend-new.onrender.com";


Khi chạy đúng, người dùng có thể:

Nói trực tiếp → Backend gửi audio lên Whisper → Trả lại text

Chat hoặc nghe → ThamAI phản hồi bằng giọng tự nhiên

🔧 Thư viện sử dụng
Tên gói	Mô tả
flask	Web framework nhẹ, dễ triển khai
flask-cors	Cho phép frontend khác domain gọi API
openai	Gọi mô hình GPT
requests	Gửi dữ liệu audio tới Whisper miễn phí
python-dotenv	Đọc file .env
gunicorn	Dùng khi deploy lên Render
⚠️ Ghi chú kỹ thuật

Khi dùng Whisper miễn phí, nếu HuggingFace chậm → nên hiển thị “Đang nhận diện…” ở frontend.

Với khóa OpenAI miễn phí hoặc hết hạn, /chat có thể báo lỗi insufficient_quota.

Trong giai đoạn test, chỉ nên gửi file ghi âm nhỏ (<10MB).

🧑‍💻 Tác giả

Hoàng Ngọc Thắm (Thắm Tạo KT)
Phát triển backend: ChatGPT (GPT-5)

“ThamAI – Trợ lý AI biết nghe, biết nói, biết lắng nghe cảm xúc.” 💖