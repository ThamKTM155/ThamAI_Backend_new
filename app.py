from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
import openai
from gtts import gTTS
from pydub import AudioSegment
import tempfile

# --- Tải biến môi trường ---
load_dotenv()

app = Flask(__name__)
CORS(app)

# --- Thiết lập OpenAI API ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Route kiểm tra trạng thái ---
@app.route('/')
def home():
    return jsonify({"message": "ThamAI Backend is running on Render ✅"})

# --- Route Chat chính ---
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "Thiếu nội dung message!"}), 400

        # Gọi GPT-5 (hoặc model tương thích)
        response = openai.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý ảo ThạchAI, lịch sự, chuyên nghiệp và thân thiện."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Route mô phỏng Whisper (nhận dạng giọng nói) ---
@app.route('/whisper', methods=['POST'])
def whisper():
    """
    Mô phỏng nhận dạng giọng nói (thay thế Whisper thật)
    Nếu gửi file .wav hoặc .mp3, trả về text giả lập.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Chưa gửi file âm thanh!"}), 400

        audio_file = request.files['file']
        filename = audio_file.filename

        # Ở bản thật sẽ dùng model Whisper của OpenAI
        # Hiện tại mô phỏng nhận dạng
        text_fake = f"[Giả lập Whisper] Đã nhận file: {filename}"
        return jsonify({"text": text_fake})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Route mô phỏng Text-to-Speech bằng gTTS ---
@app.route('/speak', methods=['POST'])
def speak():
    """
    Nhận text -> Trả về file âm thanh mp3
    """
    try:
        data = request.get_json()
        text = data.get("text", "")
        if not text:
            return jsonify({"error": "Thiếu nội dung text!"}), 400

        # Tạo giọng nói với gTTS (giọng nữ mặc định)
        tts = gTTS(text=text, lang='vi')
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_file.name)

        # Trả về file âm thanh để frontend phát
        return send_file(temp_file.name, mimetype='audio/mpeg')

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Route tương thích frontend cũ ---
@app.route("/chat", methods=["POST"])
def chat_compat():
    return chat()


# --- Khởi động server ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
