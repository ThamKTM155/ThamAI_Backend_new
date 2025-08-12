from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import openai

# Nạp biến môi trường từ file .env
load_dotenv()

# Lấy API key từ biến môi trường
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Mở toàn quyền CORS (mọi domain đều truy cập được)
CORS(app, resources={r"/*": {"origins": "*"}})

# Route kiểm tra backend sống
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "✅ ThamAI backend is running."})

# Route xử lý chat
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
print("DEBUG RAW DATA:", request.data)
print("DEBUG PARSED JSON:", data)

        # Kiểm tra dữ liệu hợp lệ
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' in request"}), 400

        user_message = data["message"]

        # Gọi API OpenAI
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là ThamAI, trợ lý ảo thân thiện và hữu ích."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})

    except Exception as e:
        # Trả lỗi chi tiết để dễ debug
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Chạy local
    app.run(host="0.0.0.0", port=5000, debug=True)
