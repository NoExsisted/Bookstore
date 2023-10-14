import requests

base_url = "http://127.0.0.1:3000/auth"
register_data = {"user_id": "txh", "password": "123456"}
response = requests.post(f"{base_url}/register", json=register_data)

print(response.status_code)
print(response.json())
