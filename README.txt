# 🧠 ThamAI Ultra+ v1.4 Backend (Flask)

## Cài đặt nhanh
1. Tạo thư mục backend, ví dụ: ThamAI_Backend_ultra
2. Dán 3 file: app.py, requirements.txt, README.txt
3. (Tuỳ chọn) Tạo môi trường ảo:
   python -m venv venv
   venv\Scripts\activate
4. Cài thư viện:
   pip install -r requirements.txt
5. Chạy thử cục bộ:
   python app.py
   → mở http://127.0.0.1:5000/ trên trình duyệt để test.

## Triển khai trên Render
1. Push toàn bộ thư mục backend lên GitHub.
2. Truy cập https://dashboard.render.com/
3. New Web Service → Chọn repo backend → Environment = Python
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app:app`
6. Deploy → Lưu ý domain backend ví dụ:
   https://thamai-backend-new.onrender.com

## Kiểm tra kết nối
Mở trình duyệt:
https://thamai-backend-new.onrender.com/
→ Nếu thấy: {"status":"ok","message":"ThamAI Ultra+ backend is running!"}
Là thành công ✅

## API routes
| Route     | Mô tả                          | Method |
|------------|-------------------------------|---------|
| `/`        | Kiểm tra backend              | GET     |
| `/chat`    | Nhận text, trả phản hồi giả lập | POST    |
| `/speak`   | Text → giọng nói (gTTS)       | POST    |
| `/whisper` | Ghi âm → văn bản mô phỏng     | POST    |

---

## Gợi ý kiểm thử
### 1. Chat:
