# =========================
# 💬 Trợ lý ThamAI Backend (Flask + OpenAI)
# =========================

from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import base64
import io
from pathlib import Path

app = Flask(__name__)
CORS(app)

# --- Cấu hình API key ---
import os
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Route kiểm tra kết nối ---
@app.route('/test', methods=['GET'])
def test_connection():
    return jsonify({"message": "✅ Kết nối backend ThamAI thành công!", "status": "ok"}), 200


# --- Route trò chuyện chính ---
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "❌ Không nhận được tin nhắn."}), 400

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": f"Lỗi xử lý chat: {str(e)}"}), 500


# --- Route TTS: Text -> Giọng nói ---
@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "Không có nội dung để đọc."}), 400

    try:
        # Sử dụng model TTS của OpenAI
        tts_response = openai.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",   # alloy / verse / coral / sage
            input=text
        )

        audio_bytes = tts_response.read()
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        return jsonify({"audio": audio_base64})
    except Exception as e:
        return jsonify({"error": f"Lỗi TTS: {str(e)}"}), 500


# --- Route Whisper: Ghi âm -> Văn bản ---
@app.route('/whisper', methods=['POST'])
def whisper():
    if 'audio' not in request.files:
        return jsonify({"error": "Không có file ghi âm gửi lên."}), 400

    audio_file = request.files['audio']

    try:
        # Whisper API - tự động nhận dạng tiếng Việt
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return jsonify({"text": transcript.text})
    except Exception as e:
        return jsonify({"error": f"Lỗi Whisper: {str(e)}"}), 500


# --- Chạy ứng dụng ---
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
