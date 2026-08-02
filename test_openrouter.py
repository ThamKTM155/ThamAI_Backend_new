import requests
import os
from dotenv import load_dotenv

load_dotenv()

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "openai/gpt-3.5-turbo",
    "messages": [
        {
            "role": "user",
            "content": "Xin chào"
        }
    ]
}

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers=headers,
    json=payload
)

print(response.status_code)
print(response.text)