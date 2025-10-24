from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from gtts import gTTS
import os
import tempfile

app = Flask(__name__)
CORS(app)  # Cho phép frontend (Vercel) truy cập

@app.route('/')
def home():
    return jsonify({"message": "Backend ThamAI hoạt động tốt!"})

# 🧠 Route CHAT
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({"reply": "Xin vui lòng nhập nội dung."})
    reply = f"ThamAI: Tôi đã nhận được - '{user_message}'"
    return jsonify({"reply": reply})

# 🎙️ Route WHISPER (giả lập nhận diện giọng nói)
@app.route('/whisper', methods=['POST'])
def whisper():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Không có file ghi âm nào được gửi."}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Tên file rỗng."}), 400

        # Giả lập nhận diện: chỉ trả về chuỗi mô phỏng
        return jsonify({"text": "Xin chào, đây là mô phỏng Whisper!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔊 Route SPEAK (phát giọng bằng gTTS)
@app.route('/speak', methods=['POST'])
def speak():
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({"error": "Không có nội dung để đọc."}), 400

        # Tạo file tạm
        tts = gTTS(text, lang='vi')
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp.name)

        return send_file(temp.name, mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
