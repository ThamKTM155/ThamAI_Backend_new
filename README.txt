==========================
THAMAI BACKEND - HƯỚNG DẪN SỬ DỤNG
==========================

📍 MỤC ĐÍCH:
Backend Flask cho Trợ lý ảo ThamAI, chạy trên Render.
Bao gồm:
- ChatGPT API (/api/chat)
- Nhận dạng giọng nói (/whisper - mô phỏng)
- Phát giọng nói ThạchAI (/speak - dùng gTTS)

----------------------------
1️⃣ CẤU TRÚC THƯ MỤC
----------------------------
ThamAI_Backend_new/
│
├── app.py
├── requirements.txt
├── .env
└── README.txt

----------------------------
2️⃣ NỘI DUNG FILE .env
----------------------------
OPENAI_API_KEY=sk-xxxxxx
RENDER_EXTERNAL_URL=https://thamai-backend-new.onrender.com

----------------------------
3️⃣ CÁCH CHẠY LOCAL
----------------------------
Bước 1: Cài thư viện
    pip install -r requirements.txt

Bước 2: Chạy thử
    python app.py

Bước 3: Mở trình duyệt:
    http://127.0.0.1:5000

----------------------------
4️⃣ TRIỂN KHAI LÊN RENDER
----------------------------
1. Push repo này lên GitHub
2. Vào https://render.com > New Web Service
3. Chọn repo ThamAI_Backend_new
4. Build Command:
       pip install -r requirements.txt
5. Start Command:
       gunicorn app:app
6. Sau khi deploy, backend sẽ có URL ví dụ:
       https://thamai-backend-new.onrender.com

----------------------------
5️⃣ KIỂM TRA CÁC API
----------------------------
- Kiểm tra trạng thái:
  🔗 GET /
  → {"message": "ThamAI Backend is running on Render ✅"}

- Gửi chat:
  🔗 POST /api/chat
  Body: {"message": "Xin chào!"}
  → {"reply": "Chào bạn, tôi là ThạchAI..."}

- Gửi giọng nói mô phỏng:
  🔗 POST /speak
  Body: {"text": "Xin chào, tôi là ThạchAI"}
  → Trả về file mp3 phát giọng nói

- Gửi âm thanh nhận dạng (mô phỏng):
  🔗 POST /whisper
  (Gửi file âm thanh .wav)
  → {"text": "Nội dung được nhận dạng..."}
  
----------------------------
6️⃣ LIÊN KẾT FRONTEND
----------------------------
- File script.js nên dùng endpoint backend:
  const BACKEND_URL = "https://thamai-backend-new.onrender.com";

- Gọi API:
  fetch(`${BACKEND_URL}/api/chat`, {...})
  fetch(`${BACKEND_URL}/speak`, {...})
  fetch(`${BACKEND_URL}/whisper`, {...})

----------------------------
✅ HOÀN THÀNH
----------------------------
Sau khi kiểm tra đủ 3 route hoạt động (chat, speak, whisper),
frontend có thể kết nối và sử dụng được đầy đủ các tính năng:
- ThạchAI nghe – hiểu – trả lời – nói chuyện bằng giọng nữ/nam.

Người thực hiện: ChatGPT (hỗ trợ Anh Hoàng Ngọc Thắm)
Ngày cập nhật: 24/10/2025
==========================
