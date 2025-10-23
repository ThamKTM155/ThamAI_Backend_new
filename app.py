# =========================================
# 🎯 ThamAI Backend - Flask Server
# Phiên bản: 2025-10
# Mục tiêu: Chat + Text-to-Speech + Speech-to-Text
# =========================================

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import openai, os
from tempfile import NamedTemporaryFile

# --- Nạp biến môi trường ---
load_dotenv()

# --- Khởi tạo Flask ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- API Key OpenAI ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("⚠️ Cảnh báo: Chưa có API Key trong .env")
client = openai.OpenAI(api_key=OPENAI_API_KEY)


# -------------------------
# Route: Kiểm tra kết nối
# -------------------------
@app.route('/test', methods=['GET'])
def test_connection():
    return jsonify({
        "message": "✅ Kết nối backend ThamAI thành công!",
        "status": "ok"
    }), 200


# -------------------------
# Route: Chat (Văn bản ↔ Văn bản)
# -------------------------
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        if not message:
            return jsonify({"error": "Thiếu nội dung tin nhắn"}), 400

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Bạn là trợ lý thân thiện tên ThamAI, nói năng nhẹ nhàng, vui vẻ, "
                        "có thể trả lời bằng giọng Nam hoặc Nữ tùy yêu cầu người dùng."
                    )
                },
                {"role": "user", "content": message}
            ]
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        print("❌ Lỗi /chat:", e)
        return jsonify({"error": str(e)}), 500


# -------------------------
# Route: Chuyển văn bản → giọng nói (Text → Speech)
# -------------------------
@app.route('/speak', methods=['POST'])
def speak():
    try:
        data = request.get_json()
        text = data.get("text", "")
        if not text:
            return jsonify({"error": "Thiếu nội dung văn bản"}), 400

        # Gọi OpenAI TTS (Text-to-Speech)
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="nova",  # ✅ Giọng nữ mềm mại tự nhiên
            input=text
        )

        # Ghi file tạm và phát lại
        with NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            response.stream_to_file(tmp.name)
            tmp.flush()
            return send_file(tmp.name, mimetype="audio/mpeg")

    except Exception as e:
        print("❌ Lỗi /speak:", e)
        return jsonify({"error": str(e)}), 500
# -------------------------
# Chạy local (tùy chọn)
# -------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
