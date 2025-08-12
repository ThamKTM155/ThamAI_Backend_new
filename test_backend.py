import requests

url = "https://thamai-backend-new.onrender.com/chat"
data = {
    "message": "Chào trợ lý, hôm nay bạn thế nào?"
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)

print("Status code:", response.status_code)
print("Response JSON:", response.json())
