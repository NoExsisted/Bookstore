from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import random
import string

client = MongoClient('localhost', 27017)
users = client.bookstore.users
app = Flask(__name__)

def generate_token():
    # 生成随机的访问令牌
    token = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
    return token

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    user_id = data.get("user_id")
    password = data.get("password")

    # 检查用户是否已存在
    if users.find_one({"user_id": user_id}):
        return jsonify({"message": "用户名重复"}), 500
    # 插入用户数据
    users.insert_one({"user_id": user_id, "password": password})

    return jsonify({"message": "ok"}), 200

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    user_id = data.get("user_id")
    password = data.get("password")

    user = users.find_one({"user_id": user_id})

    if user and user["password"] == password:
        # 登录成功，生成访问令牌
        token = generate_token()
        return jsonify({"message": "ok", "token": token}), 200
    else:
        return jsonify({"message": "用户名或密码错误"}), 401

@app.route("/auth/password", methods=["POST"])
def change_password():
    data = request.get_json()
    user_id = data.get("user_id")
    old_password = data.get("oldPassword")
    new_password = data.get("newPassword")

    user = users.find_one({"user_id": user_id})

    if user and user["password"] == old_password:
        # 更新密码
        users.update_one({"user_id": user_id}, {"$set": {"password": new_password}})
        return jsonify({"message": "ok"}), 200
    else:
        return jsonify({"message": "更改密码失败"}), 401

@app.route("/auth/unregister", methods=["POST"])
def unregister():
    data = request.get_json()
    user_id = data.get("user_id")
    password = data.get("password")

    user = users.find_one({"user_id": user_id})

    if user and user["password"] == password:
        # 删除用户
        users.delete_one({"user_id": user_id})
        return jsonify({"message": "ok"}), 200
    else:
        return jsonify({"message": "注销失败，用户名不存在或密码不正确"}), 401

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=3000)
