# from flask import Blueprint, Flask
# from pymongo import MongoClient
#
# client = MongoClient('localhost', 27017)
# db = client.bookstore
#
# app = Flask(__name__)
#
# if __name__ == "__main__":
#     app.run(host='127.0.0.1', port=5000)


from flask import Flask, request, jsonify

app = Flask(__name__)

error_code = {
    401: "authorization fail.",
    511: "non exist user id {}",
    512: "exist user id {}",
    513: "non exist store id {}",
    514: "exist store id {}",
    515: "non exist book id {}",
    516: "exist book id {}",
    517: "stock level low, book id {}",
    518: "invalid order id {}",
    519: "not sufficient funds, order id {}",
    520: "",
    521: "",
    522: "",
    523: "",
    524: "",
    525: "",
    526: "",
    527: "",
    528: "",
}


def error_non_exist_user_id(user_id):
    return 511, error_code[511].format(user_id)


def error_exist_user_id(user_id):
    return 512, error_code[512].format(user_id)


def error_non_exist_store_id(store_id):
    return 513, error_code[513].format(store_id)


def error_exist_store_id(store_id):
    return 514, error_code[514].format(store_id)


def error_non_exist_book_id(book_id):
    return 515, error_code[515].format(book_id)


def error_exist_book_id(book_id):
    return 516, error_code[516].format(book_id)


def error_stock_level_low(book_id):
    return 517, error_code[517].format(book_id)


def error_invalid_order_id(order_id):
    return 518, error_code[518].format(order_id)


def error_not_sufficient_funds(order_id):
    return 519, error_code[518].format(order_id)


def error_authorization_fail():
    return 401, error_code[401]


def error_and_message(code, message):
    return code, message


import jwt
import time
import logging
from pymongo import MongoClient

# from be.model import db_conn
# import error

class User:
    token_lifetime: int = 3600  # 3600 seconds

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']
        # db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt.decode(token, key=user_id, algorithms="HS256")
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    @staticmethod
    def jwt_encode(user_id: str, terminal: str) -> str:
        encoded = jwt.encode(
            {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
            key=user_id,
            algorithm="HS256",
        )
        return encoded

    def jwt_decode(encoded_token, user_id: str) -> str:
        decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
        return decoded

    def register(self, user_id: str, password: str):
        # 检查用户是否已存在
        user = self.db.users.find_one({"user_id": user_id})
        if user is not None:
            return error_exist_user_id(user_id)

        # 用户不存在，进行注册
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = self.jwt_encode(user_id, terminal)
            user_data = {
                "user_id": user_id,
                "password": password,
                "balance": 0,
                "token": token,
                "terminal": terminal,
            }
            self.db.users.insert_one(user_data)
        except Exception as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        user = self.db.users.find_one({"user_id": user_id})
        if user is None:
            return error_authorization_fail()
        db_token = user.get("token")
        if not self.__check_token(user_id, db_token, token):
            return error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        user = self.db.users.find_one({"user_id": user_id})
        if user is None:
            return error_authorization_fail()
        db_password = user.get("password")
        if password != db_password:
            return error_authorization_fail()
        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = self.jwt_encode(user_id, terminal)
            self.db.users.update_one({"user_id": user_id}, {"$set": {"token": token, "terminal": terminal}})
        except Exception as e:
            return 528, "{}".format(str(e)), ""
        return 200, "ok", token

    # def login(self, user_id: str, password: str) -> (int, str, str):
    #     token = ""
    #     try:
    #         code, message = self.check_password(user_id, password)
    #         if code != 200:
    #             return code, message, ""
    #
    #         terminal = "terminal_{}".format(str(time.time()))  # 自动生成终端信息
    #         token = self.jwt_encode(user_id, terminal)
    #         self.db.users.update_one({"user_id": user_id}, {"$set": {"token": token, "terminal": terminal}})
    #     except Exception as e:
    #         return 528, "{}".format(str(e)), ""
    #     return 200, "ok", token

    # def logout(self, user_id: str, token: str) -> bool:
    #     try:
    #         code, message = self.check_token(user_id, token)
    #         if code != 200:
    #             return code, message
    #
    #         terminal = "terminal_{}".format(str(time.time()))
    #         dummy_token = self.jwt_encode(user_id, terminal)
    #
    #         self.db.users.update_one({"user_id": user_id}, {"$set": {"token": dummy_token, "terminal": terminal}})
    #     except Exception as e:
    #         return 528, "{}".format(str(e))
    #     return 200, "ok"
    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = self.jwt_encode(user_id, terminal)

            self.db.users.update_one({"user_id": user_id}, {"$set": {"token": dummy_token, "terminal": terminal}})
        except Exception as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            self.db.users.delete_one({"user_id": user_id})
        except Exception as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

    def change_password(self, user_id: str, old_password: str, new_password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = self.jwt_encode(user_id, terminal)
            self.db.users.update_one({"user_id": user_id},
                                     {"$set": {"password": new_password, "token": token, "terminal": terminal}})
        except Exception as e:
            return 528, "{}".format(str(e))
        return 200, "ok"


@app.route("/auth/login", methods=["POST"])
def login():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    terminal = request.json.get("terminal", "")
    u = User()
    code, message, token = u.login(
        user_id=user_id, password=password, terminal=terminal
    )
    return jsonify({"message": message, "token": token}), code


@app.route("/auth/logout", methods=["POST"])
def logout():
    user_id: str = request.json.get("user_id")
    token: str = request.headers.get("token")
    u = User()
    code, message = u.logout(user_id=user_id, token=token)
    return jsonify({"message": message}), code


@app.route("/auth/register", methods=["POST"])
def register():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = User()
    code, message = u.register(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@app.route("/auth/unregister", methods=["POST"])
def unregister():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = User()
    code, message = u.unregister(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@app.route("/auth/password", methods=["POST"])
def change_password():
    user_id = request.json.get("user_id", "")
    old_password = request.json.get("oldPassword", "")
    new_password = request.json.get("newPassword", "")
    u = User()
    code, message = u.change_password(
        user_id=user_id, old_password=old_password, new_password=new_password
    )
    return jsonify({"message": message}), code

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
