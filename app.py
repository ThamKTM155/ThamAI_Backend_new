from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

from utils.logger import logger
from config.settings import OPENROUTER_API_KEY


from utils.rule_engine import (
    check_local_response,
    memory_first,
    format_memory_reply
)
from utils.cache_engine import (
    get_cache,
    save_cache
)

MEMORY_URL = "http://127.0.0.1:5005/memory"
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
            MEMORY_URL,
            params={"q": "vợ"},
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
        # ===== BUILD-40A-05 : Identity API =====

        try:

            identity = requests.get(

                "http://127.0.0.1:5005/identity",

                params={

                    "q": message

                },

                timeout=3

            )

            identity_reply = identity.json().get(

                "answer",

                ""

            )

            if identity_reply:

                return jsonify({

                    "reply": identity_reply

                })

        except Exception:

            pass

        # ===== Hết BUILD-40A-05 =====
        # ===== BUILD-40A =====
        identity_reply = answer_identity(message)

        if identity_reply is not None:

            return jsonify({
                "reply": identity_reply
            })

        # ===== Hết BUILD-40A =====
        # ===== BUILD-39D =====

        cache_reply = get_cache(message)

        if cache_reply is not None:

            return jsonify({
                "reply": cache_reply
            })

        # ===== Hết BUILD-39D =====

        # ===== BUILD-39A =====

        local_reply = check_local_response(message)

        if local_reply is not None:

            return jsonify({
                "reply": local_reply
            })

        # ===== Hết BUILD-39A =====

        # Nếu message rỗng
        if not message:

            return jsonify({
                "reply": "Anh chưa nhập nội dung."
            })

        # ===== BUILD-38A-03 =====

        try:
            mem = requests.get(
                MEMORY_URL,
                params={"q": message},
                timeout=5
            )

            memory_context = mem.json().get("answer", "")

        except Exception as e:
            memory_context = ""
        
        # ===== Hết BUILD-38A-03 =====
        ## Đoạn từ dòng 108 đến 115 là đoạn giới hạn ký tự có thể mất tiền phí #### 1200 ký tự #####

        # ===== BUILD-38A-04 =====
        MAX_MEMORY = 1200

        if len(memory_context) > MAX_MEMORY:
            memory_context = memory_context[:MAX_MEMORY]

        # ===== Hết BUILD-38A-04 =====
        # ===== BUILD-39B =====

        memory_reply = memory_first(
            message,
            memory_context
        )

        if memory_reply is not None:

            memory_reply = format_memory_reply(memory_reply)

            return jsonify({
                "reply": memory_reply
            })

        # ===== Hết BUILD-39B =====
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
                    "content": """
                Bạn là ThamAI.

                QUY TẮC:

                1. Luôn đọc "Thông tin trong bộ nhớ" trước.
                2. Nếu bộ nhớ liên quan tới câu hỏi thì PHẢI sử dụng.
                3. Không được trả lời theo kiến thức chung khi bộ nhớ đã có câu trả lời.
                4. Nếu bộ nhớ không liên quan thì mới trả lời theo kiến thức của bạn.
                5. Không được tự bịa thêm thông tin.
                """
                },
                {
                    "role": "user",
                    "content":
                f"""Thông tin trong bộ nhớ:

                {memory_context}

                =====================

                Câu hỏi hiện tại:

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
                "reply": "OpenRouter lỗi:\n" + str(result)
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