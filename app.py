from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return {"message": "Backend ThamAI hoạt động tốt!"}

@app.route("/test")
def test():
    return {"message": "ThamAI Backend đang online"}

@app.route("/analyze_emotion", methods=["POST"])
def analyze_emotion():
    data = request.get_json()
    text = data.get("text", "").lower()

    # 🎭 Logic phân tích cảm xúc cơ bản
    if any(x in text for x in ["vui", "cười", "tuyệt", "hạnh phúc"]):
        emotion = "happy"
    elif any(x in text for x in ["buồn", "khóc", "đau", "chán"]):
        emotion = "sad"
    elif any(x in text for x in ["ngạc nhiên", "wow", "ôi", "ồ"]):
        emotion = "surprised"
    else:
        emotion = "neutral"

    return jsonify({"emotion": emotion})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
