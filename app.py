from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

# =========================
# Khởi tạo Flask
# =========================
app = Flask(__name__)
CORS(app)

# =========================
# Khởi tạo OpenAI client
# =========================
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# =========================
# Trang chủ
# =========================
@app.route("/")
def home():
    return jsonify({
        "message": "Backend ThamAI hoạt động tốt!"
    })

# =========================
# Test backend
# =========================
@app.route("/test")
def test():
    return jsonify({
        "message": "ThamAI Backend đang online"
    })

# =========================
# Chat với AI
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    if not data:
        return jsonify({
            "reply": "Không nhận được dữ liệu."
        })

    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "reply": "Anh chưa nhập nội dung."
        })

    try:

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Bạn là ThamAI, trợ lý AI nói tiếng Việt, "
                        "thân thiện, thông minh, biết trò chuyện cảm xúc "
                        "và hỗ trợ người dùng nhiệt tình."
                    )
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.7,
            max_tokens=300
        )

        reply = response.choices[0].message.content

        return jsonify({
            "reply": reply
        })

    except Exception as e:

        print("OPENAI ERROR:", str(e))

        return jsonify({
            "reply": f"Lỗi AI: {str(e)}"
        })

# =========================
# Phân tích cảm xúc
# =========================
@app.route("/analyze_emotion", methods=["POST"])
def analyze_emotion():

    data = request.get_json()
    text = data.get("text", "").lower()

    if any(x in text for x in ["vui", "cười", "tuyệt", "hạnh phúc"]):
        emotion = "happy"

    elif any(x in text for x in ["buồn", "khóc", "đau", "chán"]):
        emotion = "sad"

    elif any(x in text for x in ["ngạc nhiên", "wow", "ôi", "ồ"]):
        emotion = "surprised"

    else:
        emotion = "neutral"

    return jsonify({
        "emotion": emotion
    })

# =========================
# Chạy local
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
