from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Lấy API key từ .env
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def home():
    return jsonify({"message": "ThamAI Backend is running on Render ✅"})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "Thiếu nội dung message!"}), 400

        # Gọi model ChatGPT thực (gpt-5 hoặc gpt-4o-mini)
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý ảo ThạchAI, lịch sự, chuyên nghiệp và thân thiện."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Giữ tương thích frontend cũ (đang gọi /chat)
@app.route("/chat", methods=["POST"])
def chat_compat():
    """Giữ tương thích với frontend cũ (/chat)"""
    return chat()


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
