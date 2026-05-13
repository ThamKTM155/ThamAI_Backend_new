from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

from utils.logger import logger
from config.settings import OPENROUTER_API_KEY

# =========================
# APP
# =========================

app = Flask(__name__)
CORS(app)

logger.info("THAMAI SERVER STARTED")

# =========================
# HOME
# =========================

@app.route("/")
def home():

    return jsonify({
        "message": "ThamAI Backend hoạt động tốt!"
    })

# =========================
# TEST
# =========================

@app.route("/test")
def test():

    return jsonify({
        "message": "Backend đang online"
    })

# =========================
# HEALTH
# =========================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "ai": "online",
        "version": "v1"
    })

# =========================
# CHAT
# =========================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        # Lấy dữ liệu frontend gửi lên
        data = request.get_json(silent=True) or {}

        message = data.get("message", "").strip()

        # Nếu message rỗng
        if not message:

            return jsonify({
                "reply": "Anh chưa nhập nội dung."
            })

        # Kiểm tra API KEY
        if not OPENROUTER_API_KEY:

            return jsonify({
                "reply": "Thiếu OPENAI_API_KEY trong file .env"
            })

        # Payload gửi AI
        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content":
                    "Bạn là ThamAI, trợ lý AI thân thiện, thông minh và hỗ trợ AutoYouTube."
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        }

        # Header Authorization
        headers_data = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY.strip()}",
            "Content-Type": "application/json"
        }

        # Gửi request OpenRouter
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers_data,
            json=payload,
            timeout=60
        )

        # Response JSON
        result = response.json()

        # Nếu lỗi
        if "choices" not in result:

            return jsonify({
                "reply": str(result)
            })

        # Nội dung AI
        reply = result["choices"][0]["message"]["content"]

        return jsonify({
            "reply": reply
        })

    except Exception as e:

        print("LỖI AI:", str(e))

        return jsonify({
            "reply": f"Lỗi AI: {str(e)}"
        })

# =========================
# RUN LOCAL
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )