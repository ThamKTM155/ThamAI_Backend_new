from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from gtts import gTTS
import os
import tempfile

app = Flask(__name__)
CORS(app)

# ✅ Kiểm tra kết nối backend
@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "ThamAI Ultra+ backend is running!"})

# ✅ Route chat (giả lập phản hồi)
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    response = f"Tôi đã nhận được - '{message}'"
    return jsonify({"reply": response})

# ✅ Route speak (Text → giọng nói)
@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    text = data.get("text", "")
    lang = data.get("lang", "vi")

    tts = gTTS(text=text, lang=lang)
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmpfile.name)
    return send_file(tmpfile.name, mimetype="audio/mpeg", as_attachment=False)

# ✅ Route whisper (Voice → Text, mô phỏng)
@app.route("/whisper", methods=["POST"])
def whisper():
    if "file" not in request.files:
        return jsonify({"error": "No audio file"}), 400
    file = request.files["file"]
    filename = file.filename
    # mô phỏng xử lý
    text_result = "Xin chào, tôi là mô phỏng Whisper!"
    return jsonify({"text": text_result, "filename": filename})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
