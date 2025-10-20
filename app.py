import os, time, uuid, logging, requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI

# ==========================
# Cấu hình
# ==========================
load_dotenv()
app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
HF_API_URL = os.getenv("HF_API_URL", "https://api-inference.huggingface.co/models/openai/whisper-tiny")
HF_API_KEY = os.getenv("HF_API_KEY")

# Cấu hình logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
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
def on_error(e):
    logger.exception(f"rid={getattr(request,'_rid','-')} error: {e}")
    return jsonify({"error": str(e), "rid": getattr(request, "_rid", "-")}), 500

# ==========================
# Health check
# ==========================
@app.get("/healthz")
def health():
    return jsonify({"status": "ok", "version": "1.0.1"})

# ==========================
# Chat
# ==========================
chat_logs = []

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"reply": "⚠️ Bạn chưa nhập nội dung."})

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
        return jsonify({"reply": f"❌ Lỗi server: {str(e)}"})

# ==========================
# Logs
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
# Speech-to-Text (Hugging Face Whisper)
# ==========================
@app.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Thiếu file audio"}), 400

        file = request.files["file"]
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}

        logger.info("⏳ Gửi audio đến Hugging Face Whisper...")
        resp = requests.post(HF_API_URL, headers=headers, files={"file": (file.filename, file.read())})

        if resp.status_code != 200:
            logger.error(f"HuggingFace trả lỗi {resp.status_code}: {resp.text}")
            return jsonify({"error": f"HuggingFace error {resp.status_code}", "details": resp.text}), 500

        result = resp.json()
        text = result.get("text") or "[Không nhận diện được giọng nói]"
        logger.info(f"✅ Nhận dạng xong: {text}")

        return jsonify({"text": text})

    except Exception as e:
        logger.exception(f"Lỗi trong /speech-to-text: {e}")
        return jsonify({"error": f"Lỗi: {str(e)}"}), 500

# ==========================
# Run server
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
