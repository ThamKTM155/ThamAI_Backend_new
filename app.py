# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import logging

# =========================
# Cấu hình logging
# =========================
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# =========================
# Khởi tạo Flask
# =========================
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Trả JSON tiếng Việt chuẩn UTF-8

# =========================
# Cấu hình CORS cho frontend
# =========================
# Cho phép mọi domain truy cập (hoặc giới hạn domain của anh)
CORS(app, resources={r"/*": {"origins": "*"}})

# =========================
# API Key OpenAI
# =========================
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logging.error("⚠️ Thiếu biến môi trường OPENAI_API_KEY")
    raise RuntimeError("Thiếu OPENAI_API_KEY, hãy cấu hình trong Render hoặc file .env")

# =========================
# Route kiểm tra server
# =========================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Backend is running",
        "service": "ThamAI",
        "version": "1.0.0"
    }), 200

# =========================
# Route xử lý chat
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Lấy raw data để debug
        raw_data = request.data.decode("utf-8", errors="replace")
        logging.debug(f"📥 Raw request body: {raw_data}")

        # Parse JSON
        data = request.get_json(force=True, silent=True)
        logging.debug(f"📦 Parsed JSON: {data}")

        # Kiểm tra dữ liệu
        if not data or "message" not in data:
            logging.warning("❌ Thiếu 'message' trong request")
            return jsonify({
                "error": "Missing 'message' in request",
                "raw": raw_data
            }), 400

        user_message = str(data["message"]).strip()
        logging.info(f"💬 User: {user_message}")

        if not user_message:
            return jsonify({"error": "'message' is empty"}), 400

        # =========================
        # Gọi OpenAI
        # =========================
        logging.debug("⏳ Đang gọi API OpenAI...")
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là ThamAI, trợ lý ảo thân thiện và hữu ích."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content.strip()
        logging.info(f"🤖 AI: {reply}")

        return jsonify({"reply": reply}), 200

    except Exception as e:
        logging.exception("💥 Lỗi khi xử lý /chat")
        return jsonify({"error": str(e)}), 500

# =========================
# Main entry (local)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logging.info(f"🚀 Server running on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
