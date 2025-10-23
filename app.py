import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# -------------------------
# ⚙️ Cấu hình Flask + OpenAI
# -------------------------
app = Flask(__name__)
CORS(app)
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# 🧭 Route gốc (kiểm tra kết nối)
# -------------------------
@app.route("/", methods=["GET"])
@app.route("/test", methods=["GET"])
def home():
    return jsonify({
        "message": "✅ Kết nối backend ThamAI thành công!",
        "status": "ok"
    })

# -------------------------
# 💬 1️⃣ ChatGPT - Xử lý hội thoại
# -------------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Tin nhắn trống."}), 400

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là ThamAI - trợ lý ảo thân thiện, giọng nam miền Nam, nói chuyện vui vẻ, lịch sự và dễ hiểu."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = completion.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        print("❌ Lỗi chat:", e)
        return jsonify({"error": str(e)}), 500

# -------------------------
# 🎙️ 2️⃣ Whisper - Ghi âm → Văn bản
# -------------------------
@app.route("/whisper", methods=["POST"])
def whisper_transcribe():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Không có file ghi âm."}), 400

        audio_file = request.files["file"]
        if audio_file.filename == "":
            return jsonify({"error": "File rỗng."}), 400

        # ✅ Lưu file tạm để gửi cho OpenAI
        temp_path = "temp_input.webm"
        audio_file.save(temp_path)

        print(f"📥 Nhận file ghi âm: {audio_file.filename}, loại: {audio_file.content_type}")

        with open(temp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )

        os.remove(temp_path)
        return jsonify({"text": transcript.text})

    except Exception as e:
        print("❌ Lỗi Whisper:", e)
        return jsonify({"error": str(e)}), 500

# -------------------------
# 🔊 3️⃣ TTS - Văn bản → Giọng nói
# -------------------------
@app.route("/speak", methods=["POST"])
def speak():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "Không có nội dung để đọc."}), 400

        print(f"🔊 Tạo giọng nói cho đoạn: {text[:50]}...")

        speech = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text
        )

        return Response(speech.read(), mimetype="audio/mpeg")

    except Exception as e:
        print("❌ Lỗi tạo giọng nói:", e)
        return jsonify({"error": str(e)}), 500

# -------------------------
# 🚀 Khởi chạy Flask (local)
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
