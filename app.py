from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import openai
import os
from dotenv import load_dotenv

# ----------------------------
# 1️⃣ Nạp biến môi trường
# ----------------------------
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

HF_API_URL = os.getenv("HF_API_URL")
HF_API_KEY = os.getenv("HF_API_KEY")

# ----------------------------
# 2️⃣ Khởi tạo Flask app
# ----------------------------
app = Flask(__name__)
CORS(app)

# ----------------------------
# 3️⃣ API Chat (Text)
# ----------------------------
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "Thiếu nội dung tin nhắn"}), 400

        # Gọi OpenAI Chat Completion
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )

        reply = response["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------
# 4️⃣ API Speech-to-Text (Whisper qua Hugging Face)
# ----------------------------
@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "Không có file audio"}), 400

        audio_file = request.files['audio']
        audio_bytes = audio_file.read()

        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        response = requests.post(HF_API_URL, headers=headers, data=audio_bytes)

        if response.status_code != 200:
            return jsonify({"error": f"Lỗi Hugging Face: {response.text}"}), response.status_code

        result = response.json()

        # Hugging Face Whisper trả về text khác nhau tuỳ model
        if isinstance(result, list) and len(result) > 0 and "text" in result[0]:
            text = result[0]["text"]
        elif "text" in result:
            text = result["text"]
        else:
            text = "Không nhận diện được âm thanh."

        return jsonify({"text": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------
# 5️⃣ Khởi chạy cục bộ
# ----------------------------
@app.route('/')
def home():
    return "✅ ThamAI Backend is running properly on Render!"

@app.route('/test')
def test():
    return jsonify({"status": "ok", "message": "Backend connection successful!"})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
