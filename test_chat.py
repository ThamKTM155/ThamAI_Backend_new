import requests

r = requests.post(
    "http://127.0.0.1:5000/chat",
    json={
        "message":"Hôm nay trời thế nào?"
    }
)
print(r.json())