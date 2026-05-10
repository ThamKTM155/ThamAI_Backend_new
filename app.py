from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)

# Gemini API
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)
genai.GenerativeModel("models/gemini-1.5-flash")
@app.route("/")
def home():
    return {
        "message": "Backend ThamAI hoạt động tốt!"
    }

@app.route("/test")
def test():
    return {
        "message": "ThamAI Backend đang online"
    }

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        message = data.get("message", "")

        if not message:
            return jsonify({
                "reply": "Anh chưa nhập nội dung."
            })

        response = model.generate_content(message)

        return jsonify({
            "reply": response.text
        })

    except Exception as e:
        print("LỖI GEMINI:", str(e))

        return jsonify({
            "reply": f"Lỗi AI: {str(e)}"
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
