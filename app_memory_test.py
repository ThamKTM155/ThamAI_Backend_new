#=======================================#
#app_memory_router_v1.py
#=======================================#
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
MEMORY_URL = "http://127.0.0.1:5005/memory"
from utils.logger import logger
from config.settings import OPENROUTER_API_KEY

print(
    "OPENROUTER_API_KEY =",
    repr(OPENROUTER_API_KEY)
)
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
@app.route("/memory_test")
def memory_test():

    try:

        r = requests.get(
            "http://127.0.0.1:5005/memory",
            params={"q":"vợ"},
            timeout=5
        )

        return r.json()

    except Exception as e:

        return {
            "error": str(e)
        }
# =========================
# CHAT
# =========================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        # Lấy dữ liệu frontend gửi lên
        data = request.get_json(silent=True) or {}

        message = data.get("message", "").strip()
        memory_context = ""

        try:

            mem = requests.get(
                MEMORY_URL,
                params={"q": message},
                timeout=5
            )

            memory_context = mem.json().get(
                "answer",
                ""
            )
            # =====================
            # MEMORY ROUTER V1
            # =====================

            if (
                memory_context.strip()
                and
                "Không tìm thấy thông tin liên quan"
                not in memory_context
            ):

                return jsonify({
                    "reply": memory_context
                })
        except:

            message = data.get("message", "").strip()

        if not message:

            return jsonify({
                "reply": "Anh chưa nhập nội dung."
            })

        memory_context = ""

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
                    "content":
                    f"""
                Memory Context:

                {memory_context}

                User Question:

                {message}
                """
                }
            ]
        }

        # Header Authorization
        headers_data = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY.strip()}",
            "Content-Type": "application/json"
        }

        # Gửi request OpenRouter
        print("KEY =", OPENROUTER_API_KEY[:20])
        print("HEADER =", headers_data)
        print("\n===== DEBUG =====")
        print(headers_data)
        print(payload["model"])
        print("=================\n")
        print(repr(headers_data))
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers_data,
            json=payload,
            timeout=60
        )
        print("\n===== RESPONSE =====")
        print("STATUS =", response.status_code)
        print(response.text)
        print("====================\n")
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