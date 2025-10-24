from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/")
def home():
    return jsonify({"message": "✅ ThamAI backend đang hoạt động!"})


# 🎙️ Whisper - Speech to Text
@app.route("/whisper", methods=["POST"])
def whisper():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Không tìm thấy tệp âm thanh"}), 400

        # Lấy file âm thanh và đọc vào bộ nhớ
        audio_file = request.files["file"]
        audio_bytes = audio_file.read()

        # Tạo đối tượng file-like đúng chuẩn cho OpenAI
        audio_stream = BytesIO(audio_bytes)
        audio_stream.name = "audio.wav"

        transcript = openai.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_stream
        )

        return jsonify({"text": transcript.text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 💬 Chat - Text to Text
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý ảo ThamAI, thân thiện và chuyên nghiệp."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = completion.choices[0].message.content
        return jsonify({"reply": reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔊 TTS - Text to Speech
@app.route("/tts", methods=["POST"])
def tts():
    try:
        data = request.get_json()
        text = data.get("text", "")

        response = openai.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text
        )

        audio_bytes = response.read()
        return jsonify({"audio_base64": audio_bytes.decode("ISO-8859-1")}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
