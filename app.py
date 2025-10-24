from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai
import os
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# ------------------------
# 🔹 ROUTE TEST
# ------------------------
@app.route("/test")
def test():
    return jsonify({"status": "ok", "message": "✅ Kết nối backend ThamAI thành công!"})

# ------------------------
# 💬 ROUTE CHAT
# ------------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "")
        if not message:
            return jsonify({"error": "Thiếu nội dung tin nhắn"}), 400

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là ThamAI, trợ lý ảo thân thiện và thông minh."},
                {"role": "user", "content": message},
            ],
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})

    except Exception as e:
        print("Chat Error:", str(e))
        return jsonify({"error": "Lỗi xử lý chat", "detail": str(e)}), 500

# ------------------------
# 🎙️ ROUTE WHISPER (Speech-to-Text)
# ------------------------
@app.route("/whisper", methods=["POST"])
def whisper():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Không có file âm thanh"}), 400

        audio_file = request.files["file"]

        transcript = openai.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )

        text = transcript.text.strip() if hasattr(transcript, "text") else ""
        if not text:
            return jsonify({"error": "Không nhận dạng được giọng nói"}), 422

        return jsonify({"text": text})

    except Exception as e:
        print("Whisper Error:", str(e))
        return jsonify({"error": "Lỗi khi xử lý Whisper", "detail": str(e)}), 500

# ------------------------
# 🔊 ROUTE SPEAK (Text-to-Speech)
# ------------------------
@app.route("/speak", methods=["POST"])
def speak():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"error": "Thiếu nội dung cần đọc"}), 400

        speech_response = openai.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text
        )

        audio_bytes = BytesIO(speech_response.read())
        audio_bytes.seek(0)

        return send_file(
            audio_bytes,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="output.mp3"
        )

    except Exception as e:
        print("Speak Error:", str(e))
        return jsonify({"error": "Lỗi khi xử lý TTS", "detail": str(e)}), 500

# ------------------------
# 🏁 MAIN ENTRY
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
