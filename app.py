from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import openai
import os
from dotenv import load_dotenv

# --- Tải biến môi trường ---
load_dotenv()

# --- Khởi tạo Flask app ---
app = Flask(__name__)
CORS(app)

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")
HF_API_URL = os.getenv("HF_API_URL", "https://api-inference.huggingface.co/models/openai/whisper-tiny")

openai.api_key = OPENAI_API_KEY

# --- Route kiểm tra kết nối ---
@app.route('/test', methods=['GET'])
def test_connection():
    return jsonify({"message": "Kết nối backend thành công!", "status": "ok"}), 200


# --- Route CHAT (văn bản) ---
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "")

        if not message:
            return jsonify({"error": "Không có nội dung message gửi lên!"}), 400

        # Gọi OpenAI API (nếu còn quota)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý thân thiện tên ThắmAI."},
                {"role": "user", "content": message}
            ]
        )

        reply = response.choices[0].message['content']
        return jsonify({"reply": reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Route SPEECH TO TEXT (giọng nói -> chữ) ---
@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "Không tìm thấy tệp âm thanh!"}), 400

        audio_file = request.files['audio']

        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        response = requests.post(
            HF_API_URL,
            headers=headers,
            data=audio_file.read()
        )

        if response.status_code != 200:
            return jsonify({
                "error": f"Lỗi Whisper HuggingFace: {response.status_code}",
                "details": response.text
            }), response.status_code

        result = response.json()
        text = result.get("text", "(Không nhận dạng được giọng nói)")
        return jsonify({"text": text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Chạy app ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
