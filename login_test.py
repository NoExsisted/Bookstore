import requests

# 定义您的 Flask 服务器地址
base_url = "http://127.0.0.1:3000/auth"

# 定义注册数据
register_data = {"user_id": "txh", "password": "123456"}

# 发送注册请求
response = requests.post(f"{base_url}/register", json=register_data)

# 打印响应状态码和内容
print(response.status_code)
print(response.json())
