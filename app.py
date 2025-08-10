# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import traceback
from openai import OpenAI

# Load .env when running local
load_dotenv()

# Read environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# FRONTEND_URLS: optional, comma-separated list of allowed origins.
# If not set, we'll allow all origins (useful for dev). In production set specific domain(s).
FRONTEND_URLS = os.getenv("FRONTEND_URLS", "*")

# Init Flask
app = Flask(__name__)

# Setup CORS: either specific list or allow all if FRONTEND_URLS=="*"
if FRONTEND_URLS.strip() == "*" or FRONTEND_URLS.strip() == "":
    CORS(app, resources={r"/*": {"origins": "*"}})
else:
    origins = [u.strip() for u in FRONTEND_URLS.split(",") if u.strip()]
    CORS(app, resources={r"/*": {"origins": origins}})

# Validate API key present early (fail fast)
if not OPENAI_API_KEY:
    # don't raise in production automatically; print a clear message and continue so logs show it
    print("⚠️ WARNING: OPENAI_API_KEY is not set. Set OPENAI_API_KEY in environment variables.")

# Init OpenAI client (works with openai>=1.0.0)
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "success",
        "message": "✅ ThamAI backend is running.",
        "frontend_allowed": FRONTEND_URLS
    })


@app.route("/chat", methods=["POST"])
def chat():
    try:
        if client is None:
            return jsonify({"status": "error", "message": "OPENAI_API_KEY not configured on server."}), 500

        data = request.get_json(force=True)
        user_message = data.get("message", "")
        if not user_message or not user_message.strip():
            return jsonify({"status": "error", "message": "No message provided"}), 400

        # call OpenAI via new client
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Bạn là ThamAI — trợ lý ấm áp, lịch sự, hữu dụng."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.6
        )

        # be tolerant with response shape
        try:
            ai_reply = response.choices[0].message.content.strip()
        except Exception:
            # fallback
            ai_reply = response.choices[0].message["content"].strip()

        return jsonify({"status": "success", "reply": ai_reply})

    except Exception as e:
        # print full traceback to logs on Render (do NOT print API key)
        print("🔥 Exception in /chat:", str(e))
        print(traceback.format_exc())
        # return a short safe message to client
        return jsonify({"status": "error", "message": "Server error: see server logs for details."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
