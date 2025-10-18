import os
import time
import uuid
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# ==========================
# Cấu hình ứng dụng
# ==========================
load_dotenv()
app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==========================
# Cấu hình logging
# ==========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("thamai")

@app.before_request
def before_request():
    request._t = time.time()
    request._rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())

@app.after_request
def after_request(resp):
    dt = (time.time() - getattr(request, "_t", time.time())) * 1000
    logger.info(f"rid={request._rid} {request.method} {request.path} {resp.status_code} {dt:.1f}ms")
    resp.headers["X-Request-Id"] = request._rid
    return resp

@app.errorhandler(Exception)
def handle_error(e):
    logger.exception(f"rid={getattr(request, '_rid', '-')} error: {e}")
    return jsonify({"error": "internal_error", "rid": getattr(request, "_rid", "-")}), 500

# ==========================
# Health check
# ==========================
@app.get("/healthz")
def health_check():
    return jsonify({"status": "ok", "version": "1.0.0"})

# ==========================
# Bộ nhớ logs hội thoại
# ==========================
chat_logs = []

# ==========================
# Route: Chat (Text)
# ==========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "⚠️ Bạn chưa nhập nội dung."}), 400

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là ThamAI, trợ lý AI thân thiện, nói chuyện bằng tiếng Việt."},
                {"role": "user", "content": user_message}
            ]
        )

        bot_reply = response.choices[0].message.content.strip()

        chat_logs.append({
            "user": user_message,
            "bot": bot_reply,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return jsonify({"reply": bot_reply})

    except Exception as e:
        logger.exception(f"Lỗi khi xử lý chat: {e}")
        return jsonify({"reply": f"❌ Lỗi server: {str(e)}"}), 500

# ==========================
# Route: Speech to Text
# ==========================
@app.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Thiếu file audio"}), 400

        audio_file = request.files["file"]
        temp_path = f"/tmp/{uuid.uuid4()}.webm"
        audio_file.save(temp_path)

        # Gọi Whisper để chuyển giọng nói sang văn bản
        with open(temp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=f,
                response_format="text"
            )

        os.remove(temp_path)
        return jsonify({"text": transcript.strip()})

    except Exception as e:
        logger.exception(f"Lỗi khi xử lý giọng nói: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================
# Route: Lấy và xóa lịch sử
# ==========================
@app.route("/logs", methods=["GET"])
def get_logs():
    return jsonify(chat_logs)

@app.route("/logs/clear", methods=["DELETE"])
def clear_logs():
    global chat_logs
    chat_logs = []
    return jsonify({"message": "🗑️ Lịch sử đã được xóa."})

# ==========================
# Chạy server
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
