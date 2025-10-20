# -------------------------
# Route: Chuyển văn bản thành giọng nói (Text → Speech)
# -------------------------
@app.route('/speak', methods=['POST'])
def speak():
    try:
        data = request.get_json()
        text = data.get("text", "")
        if not text:
            return jsonify({"error": "Thiếu nội dung văn bản"}), 400

        import openai, base64, io
        from flask import send_file
        from tempfile import NamedTemporaryFile

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Gọi OpenAI TTS (giọng tự nhiên)
        speech = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text
        )

        # Ghi ra file tạm rồi gửi về
        with NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(speech.read())
            tmp.flush()
            return send_file(tmp.name, mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# Route: Chuyển giọng nói thành văn bản (Speech → Text)
# -------------------------
@app.route('/whisper', methods=['POST'])
def whisper():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "Không tìm thấy file âm thanh"}), 400

        audio_file = request.files['audio']

        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Gọi OpenAI Whisper để nhận diện giọng nói
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )

        return jsonify({"text": transcript.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
