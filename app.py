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
        # In raw data từ request
        raw_data = request.data
        print("=== RAW REQUEST DATA ===")
        print(raw_data)

        # Thử parse JSON
        data = request.get_json(silent=True)
        print("=== PARSED JSON ===")
        print(data)

        # Kiểm tra dữ liệu hợp lệ
        if not data or "message" not in data:
            return jsonify({
                "error": "Missing 'message' in request",
                "raw": raw_data.decode("utf-8", errors="replace")
            }), 400

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
        import traceback
        error_info = traceback.format_exc()
        print("=== ERROR ===")
        print(error_info)
        return jsonify({"error": str(e), "trace": error_info}), 500

