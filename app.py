import os
import logging, time, uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI
import requests

# ==========================
# Cấu hình
# ==========================
load_dotenv()
app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
HF_API_URL = os.getenv("HF_API_URL")
HF_API_KEY = os.getenv("HF_API_KEY")

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("thamai")

# ==========================
# Trước & Sau mỗi request
# ==========================
@app.before_request
def _prep():
    request._t = time.time()
    request._rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())

@app.after_request
def _access_log(resp):
    dt = (time.time() - getattr(request, "_t", time.time())) * 1000
    logger.info(f"rid={request._rid} {request.method} {request.path} {resp.status_code} {dt:.1f}ms")
    resp.headers["X-Request-Id"] = request._rid
    return resp

@app.errorhandler(Exception)
def _err(e):
    logger.exception(f"rid={getattr(request,'_rid','-')} error: {e}")
    return jsonify({"error": "lỗi_nội_bộ", "rid": getattr(request,'_rid','-')}), 500

# ==========================
# Health check
# ==========================
@app.route("/")
def home():
    return "✅ ThamAI Backend is running properly on Render!"

@app.route("/test")
def test():
    return jsonify({"status": "ok", "message": "Backend connection successful!"})

# ==========================
# Bộ nhớ tạm hội thoại
# ==========================
chat_logs = []

# ==========================
# Route: Chat
# ==========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "⚠️ Bạn chưa nhập nội dung."})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là ThamAI – trợ lý thân thiện nói tiếng Việt, giọng vui vẻ, tự nhiên."},
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

# ==========================
# Route: Speech-to-Text (Whisper)
# ==========================
@app.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    if "audio" not in request.files:
        return jsonify({"error": "Thiếu tệp âm thanh"}), 400

    audio_file = request.files["audio"]

    try:
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        resp = requests.post(HF_API_URL, headers=headers, data=audio_file.read())
        text = resp.text
        return jsonify({"text": text})
    except Exception as e:
        logger.exception("Speech-to-text error")
        return jsonify({"error": str(e)}), 500

# ==========================
# Route: Text-to-Speech (OpenAI TTS)
# ==========================
@app.route("/text-to-speech", methods=["POST"])
def text_to_speech():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Không có nội dung văn bản."}), 400

    try:
        speech_file = f"speech_{uuid.uuid4().hex}.mp3"
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text
        ) as response:
            response.stream_to_file(speech_file)
        return jsonify({"audio_url": f"/static/{speech_file}"})
    except Exception as e:
        logger.exception("TTS error")
        return jsonify({"error": str(e)}), 500

# ==========================
# Route: Lịch sử chat
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
# Run server
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
