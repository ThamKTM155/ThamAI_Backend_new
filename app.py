from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.route("/")
def home():
    return {
        "message": "ThamAI Backend hoạt động tốt!"
    }

@app.route("/test")
def test():
    return {
        "message": "Backend đang online"
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

        response = requests.post(

            "https://openrouter.ai/api/v1/chat/completions",

            headers={

                "Authorization":
                f"Bearer {OPENROUTER_API_KEY}",

                "Content-Type":
                "application/json"
            },

            json={

                "model":
                "openai/gpt-3.5-turbo",

                "messages": [

                    {
                        "role": "user",
                        "content": message
                    }
                ]
            }
        )

    result = response.json()
    
    print(result)
    
    if "choices" not in result:
    
        return jsonify({
            "reply": f"Lỗi OpenRouter: {result}"
        })
    
    reply = result["choices"][0]["message"]["content"]

        return jsonify({
            "reply": reply
        })

    except Exception as e:

        print("LỖI AI:", str(e))

        return jsonify({
            "reply": f"Lỗi AI: {str(e)}"
        })

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
