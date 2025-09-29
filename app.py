import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI

# ==========================
# Cấu hình
# ==========================
load_dotenv()
app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Bộ nhớ logs hội thoại
chat_logs = []

# ==========================
# Route: Chat
# ==========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "⚠️ Bạn chưa nhập nội dung."})

        # Gọi OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là ThamAI, trợ lý AI thân thiện, nói chuyện bằng tiếng Việt."},
                {"role": "user", "content": user_message}
            ]
        )

        bot_reply = response.choices[0].message.content.strip()

        # Lưu vào logs
        chat_logs.append({
            "user": user_message,
            "bot": bot_reply,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"reply": f"❌ Lỗi server: {str(e)}"})

# ==========================
# Route: Lấy lịch sử
# ==========================
@app.route("/logs", methods=["GET"])
def get_logs():
    return jsonify(chat_logs)

# ==========================
# Route: Xóa lịch sử
# ==========================
@app.route("/logs/clear", methods=["DELETE"])
def clear_logs():
    global chat_logs
    chat_logs = []
    return jsonify({"message": "🗑️ Lịch sử đã được xóa."})

# ==========================
# Run server
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
