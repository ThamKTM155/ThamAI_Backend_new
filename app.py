from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from utils.logger import logger
app = Flask(__name__)
CORS(app)

# =========================
# API KEY
# =========================

OPENROUTER_API_KEY = os.getenv("OPENAI_API_KEY")

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
# CHAT
# =========================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        # Lấy dữ liệu frontend gửi lên
        data = request.get_json(silent=True) or {}

        message = data.get("message", "").strip()

        # Kiểm tra message rỗng
        if not message:

            return jsonify({
                "reply": "Anh chưa nhập nội dung."
            })

        # Kiểm tra API KEY
        if not OPENROUTER_API_KEY:

            return jsonify({
                "reply": "Thiếu OPENAI_API_KEY trên Render."
            })

        # Gửi request tới OpenRouter
        response = requests.post(

            "https://openrouter.ai/api/v1/chat/completions",

            headers={

                "Authorization":
                f"Bearer {OPENROUTER_API_KEY}",

                "Content-Type":
                "application/json"
            },

            json={

                "model":
                "openai/gpt-3.5-turbo",

                "messages": [

                    {
                        "role": "system",
                        "content":
                        "Bạn là ThamAI, trợ lý AI thân thiện, thông minh, nói tiếng Việt tự nhiên và hỗ trợ phát triển hệ thống AutoYouTube."
                    },

                    {
                        "role": "user",
                        "content": message
                    }
                ]
            },

            timeout=60
        )

        # Chuyển response sang JSON
        result = response.json()

        print(result)

        # Nếu OpenRouter lỗi
        if "choices" not in result:

            return jsonify({
                "reply": str(result)
            })

        # Lấy nội dung AI trả về
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
        port=5000
    )
