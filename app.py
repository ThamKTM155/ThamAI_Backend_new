from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from gtts import gTTS
import os
import io
import openai
from dotenv import load_dotenv

# --- Tải biến môi trường ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

# --- Thư mục lưu tạm file âm thanh ---
TEMP_PATH = "temp_audio"
os.makedirs(TEMP_PATH, exist_ok=True)

# ----------------------------
# 1. Endpoint /whisper – MÔ PHỎNG Whisper thật
# ----------------------------
@app.route("/whisper", methods=["POST"])
def whisper_mock():
    try:
        # Mô phỏng quá trình nhận dạng giọng nói
        fake_text = "Xin chào, tôi là ThạchAI đây!"
        print("[Whisper mô phỏng] ->", fake_text)
        return jsonify({"text": fake_text})
    except Exception as e:
        return jsonify({"error": f"Whisper mô phỏng lỗi: {str(e)}"}), 500


# ----------------------------
# 2. Endpoint /ask – ChatGPT thật (gpt-4o-mini)
# ----------------------------
@app.route("/ask", methods=["POST"])
def ask_openai():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "Thiếu nội dung message"}), 400

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý thân thiện tên ThạchAI."},
                {"role": "user", "content": user_message}
            ],
        )

        reply = response.choices[0].message.content
        print("[ChatGPT]", reply)
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": f"Lỗi khi gọi OpenAI: {str(e)}"}), 500


# ----------------------------
# 3. Endpoint /speak – Tạo giọng nói tiếng Việt bằng gTTS
# ----------------------------
@app.route("/speak", methods=["POST"])
def speak():
    try:
        data = request.get_json()
        text = data.get("text", "")
        gender = data.get("gender", "female")  # 'female' hoặc 'male'

        if not text:
            return jsonify({"error": "Thiếu nội dung để đọc"}), 400

        # Dùng accent miền Bắc (vi-VN)
        tts = gTTS(text=text, lang="vi", slow=False)

        file_path = os.path.join(TEMP_PATH, "speech.mp3")
        tts.save(file_path)

        print(f"[TTS gTTS] Tạo file âm thanh giọng {gender} thành công.")
        return send_file(file_path, mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({"error": f"TTS lỗi khi tạo giọng: {str(e)}"}), 500


# ----------------------------
# 4. Kiểm tra hoạt động
# ----------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "✅ ThamAI Backend hoạt động ổn!",
        "endpoints": ["/whisper", "/ask", "/speak"]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
