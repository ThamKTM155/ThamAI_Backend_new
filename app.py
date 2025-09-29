from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

LOG_FILE = "conversation_logs.json"

# Hàm ghi log
def save_log(role, message):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "role": role,
        "message": message
    }
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    with open(LOG_FILE, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append(log_entry)
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)

# Route chính (chat)
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    save_log("user", user_input)

    # Giả lập trả lời (test, chưa cần OpenAI API)
    bot_reply = f"Bot đã nhận: {user_input}"
    save_log("bot", bot_reply)

    return jsonify({"reply": bot_reply})

# Route phụ lấy toàn bộ logs
@app.route("/logs", methods=["GET"])
def get_logs():
    if not os.path.exists(LOG_FILE):
        return jsonify([])
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
