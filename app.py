from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import openai
import os

# ==========================
# Cấu hình Flask
# ==========================
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Đảm bảo trả về JSON UTF-8
CORS(app, resources={r"/*": {"origins": "*"}})  # Cho phép mọi domain truy cập

# ==========================
# Cấu hình Logging
# ==========================
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

# ==========================
# Cấu hình OpenAI API key
# ==========================
openai.api_key = os.getenv("OPENAI_API_KEY")

# ==========================
# Route /chat
# ==========================
@app.route("/chat", methods=["POST"])
def chat():
    # Log dữ liệu gốc mà client gửi
    raw_data = request.get_data()
    logging.debug(f"Raw request body: {raw_data}")

    # Log header để xem encoding
    logging.debug(f"Request headers: {dict(request.headers)}")

    # Parse JSON
    try:
        data = request.get_json(force=True)
    except Exception as e:
        logging.error(f"JSON parse error: {e}")
        return jsonify({"error": "Invalid JSON"}), 400

    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' in request"}), 400

    user_message = data["message"]
    logging.debug(f"User message parsed: {user_message}")

    try:
        # Gọi API OpenAI
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là ThamAI, trợ lý ảo thân thiện và hữu ích."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content.strip()
        logging.debug(f"Reply: {reply}")

        return jsonify({"reply": reply})

    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ==========================
# Main
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
