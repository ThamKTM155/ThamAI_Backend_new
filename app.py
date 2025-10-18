import os, time, uuid, tempfile, subprocess, logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import speech_recognition as sr
from pydub import AudioSegment

# ==========================
# Cấu hình chung
# ==========================
load_dotenv()
app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==========================
# Logging
# ==========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("thamai")

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
    logger.exception(f"rid={getattr(request, '_rid', '-')} error: {e}")
    return jsonify({"error": "internal_error", "rid": getattr(request, '_rid', '-')}), 500

# ==========================
# Kiểm tra hệ thống
# ==========================
@app.get("/healthz")
def health():
    return jsonify({"status": "ok", "version": "1.0.0"})

# ==========================
# Bộ nhớ lưu hội thoại
# ==========================
chat_logs = []

# ==========================
# Route: Chat
# ==========================
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
        logger.error(f"Lỗi trong /chat: {e}")
        return jsonify({"reply": f"❌ Lỗi server: {str(e)}"})

# ==========================
# Route: Lấy lịch sử
# ==========================
@app.route("/logs", methods=["GET"])
def get_logs():
    return jsonify(chat_logs)

# ==========================
# Route: Xóa lịch sử
# ==========================
@app.route("/logs/clear", methods=["DELETE"])
def clear_logs():
    global chat_logs
    chat_logs = []
    return jsonify({"message": "🗑️ Lịch sử đã được xóa."})

# ==========================
# Route: Speech-to-Text
# ==========================
@app.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Không có tệp audio gửi lên"}), 400

        audio_file = request.files['file']

        # Lưu file webm tạm
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_webm:
            audio_file.save(temp_webm.name)
            temp_webm_path = temp_webm.name

        # Chuyển sang wav (16kHz mono)
        temp_wav_path = temp_webm_path.replace(".webm", ".wav")
        try:
            ffmpeg_cmd = ["ffmpeg", "-i", temp_webm_path, "-ar", "16000", "-ac", "1", temp_wav_path]
            subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except Exception as e:
            print("⚠️ FFmpeg lỗi, fallback Google:", e)
            sound = AudioSegment.from_file(temp_webm_path)
            sound.export(temp_wav_path, format="wav")

        # --- Ưu tiên Whisper ---
        try:
            with open(temp_wav_path, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    response_format="json"
                )
            text = transcript.text.strip() if hasattr(transcript, 'text') else transcript.get('text', '')
            return jsonify({"text": text, "engine": "whisper"})
        except Exception as e:
            print("⚠️ Whisper lỗi, fallback Google:", e)

        # --- Fallback Google SpeechRecognition ---
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_wav_path) as source:
            audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="vi-VN")
            return jsonify({"text": text, "engine": "google"})
        except sr.UnknownValueError:
            return jsonify({"text": "", "engine": "google", "error": "Không nhận diện được"}), 200

    except Exception as e:
        logger.error(f"Lỗi trong /speech-to-text: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            os.remove(temp_webm_path)
            os.remove(temp_wav_path)
        except:
            pass

# ==========================
# Run server
# ==========================
# ==========================
# Route: Speech to Text
# ==========================
@app.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Thiếu file audio"}), 400

        audio_file = request.files["file"]

        # Lưu file tạm
        temp_path = f"/tmp/{uuid.uuid4()}.webm"
        audio_file.save(temp_path)

        # Dùng Whisper để chuyển giọng nói thành văn bản
        with open(temp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",  # Model mới, nhẹ và chính xác
                file=f,
                response_format="text"
            )

        os.remove(temp_path)
        return jsonify({"text": transcript.strip()})

    except Exception as e:
        logger.exception(f"Lỗi khi xử lý giọng nói: {e}")
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
