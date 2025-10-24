# app.py
import os
import io
from tempfile import NamedTemporaryFile
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# Load env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("⚠️ Warning: OPENAI_API_KEY not set in .env")

# Flask + CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Test route
@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "✅ Kết nối backend ThamAI thành công!", "status": "ok"}), 200


# --- Chat route
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        message = (data.get("message") or "").strip()
        if not message:
            return jsonify({"error": "Thiếu nội dung tin nhắn"}), 400

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là ThamAI - trợ lý ảo thân thiện và hữu ích."},
                {"role": "user", "content": message},
            ],
        )
        reply = completion.choices[0].message.content
        return jsonify({"reply": reply}), 200

    except Exception as e:
        print("❌ Lỗi /chat:", e)
        return jsonify({"error": "Lỗi nội bộ server", "detail": str(e)}), 500


# --- Whisper (Speech -> Text)
@app.route("/whisper", methods=["POST"])
def whisper():
    try:
        # Expect form-data with field name "file"
        if "file" not in request.files:
            return jsonify({"error": "Không có file ghi âm (field 'file' missing)"}), 400

        audio_file = request.files["file"]
        if audio_file.filename == "":
            return jsonify({"error": "File rỗng"}), 400

        # Read bytes and wrap in BytesIO (OpenAI client expects bytes / io.IOBase)
        audio_bytes = audio_file.read()
        if not audio_bytes:
            return jsonify({"error": "Không đọc được file ghi âm"}), 400

        audio_io = io.BytesIO(audio_bytes)

        # Debug info
        print(f"📥 Received audio file: {audio_file.filename}, content_type={audio_file.content_type}, size={len(audio_bytes)} bytes")

        # Call OpenAI transcription
        try:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_io
            )
        except Exception as e:
            print("❌ OpenAI transcription error:", e)
            return jsonify({"error": "Whisper lỗi khi xử lý", "detail": str(e)}), 500

        text = getattr(transcript, "text", None) or transcript.get("text") if isinstance(transcript, dict) else None
        if text is None:
            # fallback: try converting to string
            return jsonify({"error": "Không lấy được văn bản từ Whisper", "detail": str(transcript)}), 500

        return jsonify({"text": text}), 200

    except Exception as e:
        print("❌ Lỗi /whisper:", e)
        return jsonify({"error": "Lỗi server khi nhận file", "detail": str(e)}), 500


# --- Speak (Text -> Speech)
@app.route("/speak", methods=["POST"])
def speak():
    try:
        data = request.get_json(force=True)
        text = (data.get("text") or "").strip()
        voice = (data.get("voice") or "alloy")  # default "alloy" (male-ish) ; frontend may pass "nova" for female

        if not text:
            return jsonify({"error": "Không có nội dung để đọc"}), 400

        try:
            # Create speech (this may raise exceptions from OpenAI)
            speech_obj = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice=voice,
                input=text
            )
        except Exception as e:
            print("❌ OpenAI TTS error:", e)
            # Try to get message from exception object
            return jsonify({"error": "TTS lỗi khi gọi API", "detail": str(e)}), 500

        # speech_obj should provide bytes via .read() or be bytes-like
        audio_bytes = None
        try:
            if hasattr(speech_obj, "read"):
                audio_bytes = speech_obj.read()
            elif isinstance(speech_obj, (bytes, bytearray)):
                audio_bytes = bytes(speech_obj)
            elif isinstance(speech_obj, dict) and "audio" in speech_obj:
                audio_bytes = speech_obj["audio"]
            else:
                # fallback: try str()
                audio_bytes = str(speech_obj).encode("utf-8")
        except Exception as e:
            print("❌ Lỗi đọc dữ liệu âm thanh:", e)
            return jsonify({"error": "Không thể đọc dữ liệu audio từ OpenAI", "detail": str(e)}), 500

        # Return audio with proper mimetype
        return Response(audio_bytes, mimetype="audio/mpeg")

    except Exception as e:
        print("❌ Lỗi /speak:", e)
        return jsonify({"error": "Lỗi server", "detail": str(e)}), 500


if __name__ == "__main__":
    # Use port 5000 locally
    app.run(host="0.0.0.0", port=5000, debug=True)
