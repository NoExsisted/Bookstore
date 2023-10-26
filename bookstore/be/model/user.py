# import jwt
# import time
# import logging
# import sqlite3 as sqlite
# from be.model import error
# from be.model import db_conn
#
# # encode a json string like:
# #   {
# #       "user_id": [user name],
# #       "terminal": [terminal code],
# #       "timestamp": [ts]} to a JWT
# #   }
#
#
# def jwt_encode(user_id: str, terminal: str) -> str:
#     encoded = jwt.encode(
#         {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
#         key=user_id,
#         algorithm="HS256",
#     )
#     return encoded.encode("utf-8").decode("utf-8")
#
#
# # decode a JWT to a json string like:
# #   {
# #       "user_id": [user name],
# #       "terminal": [terminal code],
# #       "timestamp": [ts]} to a JWT
# #   }
# def jwt_decode(encoded_token, user_id: str) -> str:
#     decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
#     return decoded
#
#
# class User(db_conn.DBConn):
#     token_lifetime: int = 3600  # 3600 second
#
#     def __init__(self):
#         db_conn.DBConn.__init__(self)
#
#     def __check_token(self, user_id, db_token, token) -> bool:
#         try:
#             if db_token != token:
#                 return False
#             jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
#             ts = jwt_text["timestamp"]
#             if ts is not None:
#                 now = time.time()
#                 if self.token_lifetime > now - ts >= 0:
#                     return True
#         except jwt.exceptions.InvalidSignatureError as e:
#             logging.error(str(e))
#             return False
#
#     def register(self, user_id: str, password: str):
#         try:
#             terminal = "terminal_{}".format(str(time.time()))
#             token = jwt_encode(user_id, terminal)
#             self.conn.execute(
#                 "INSERT into user(user_id, password, balance, token, terminal) "
#                 "VALUES (?, ?, ?, ?, ?);",
#                 (user_id, password, 0, token, terminal),
#             )
#             self.conn.commit()
#         except sqlite.Error:
#             return error.error_exist_user_id(user_id)
#         return 200, "ok"
#
#     def check_token(self, user_id: str, token: str) -> (int, str):
#         cursor = self.conn.execute("SELECT token from user where user_id=?", (user_id,))
#         row = cursor.fetchone()
#         if row is None:
#             return error.error_authorization_fail()
#         db_token = row[0]
#         if not self.__check_token(user_id, db_token, token):
#             return error.error_authorization_fail()
#         return 200, "ok"
#
#     def check_password(self, user_id: str, password: str) -> (int, str):
#         cursor = self.conn.execute(
#             "SELECT password from user where user_id=?", (user_id,)
#         )
#         row = cursor.fetchone()
#         if row is None:
#             return error.error_authorization_fail()
#
#         if password != row[0]:
#             return error.error_authorization_fail()
#
#         return 200, "ok"
#
#     def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
#         token = ""
#         try:
#             code, message = self.check_password(user_id, password)
#             if code != 200:
#                 return code, message, ""
#
#             token = jwt_encode(user_id, terminal)
#             cursor = self.conn.execute(
#                 "UPDATE user set token= ? , terminal = ? where user_id = ?",
#                 (token, terminal, user_id),
#             )
#             if cursor.rowcount == 0:
#                 return error.error_authorization_fail() + ("",)
#             self.conn.commit()
#         except sqlite.Error as e:
#             return 528, "{}".format(str(e)), ""
#         except BaseException as e:
#             return 530, "{}".format(str(e)), ""
#         return 200, "ok", token
#
    # def logout(self, user_id: str, token: str) -> bool:
    #     try:
    #         code, message = self.check_token(user_id, token)
    #         if code != 200:
    #             return code, message
    #
    #         terminal = "terminal_{}".format(str(time.time()))
    #         dummy_token = jwt_encode(user_id, terminal)
    #
    #         cursor = self.conn.execute(
    #             "UPDATE user SET token = ?, terminal = ? WHERE user_id=?",
    #             (dummy_token, terminal, user_id),
    #         )
    #         if cursor.rowcount == 0:
    #             return error.error_authorization_fail()
    #
    #         self.conn.commit()
    #     except sqlite.Error as e:
    #         return 528, "{}".format(str(e))
    #     except BaseException as e:
    #         return 530, "{}".format(str(e))
    #     return 200, "ok"
#
#     def unregister(self, user_id: str, password: str) -> (int, str):
#         try:
#             code, message = self.check_password(user_id, password)
#             if code != 200:
#                 return code, message
#
#             cursor = self.conn.execute("DELETE from user where user_id=?", (user_id,))
#             if cursor.rowcount == 1:
#                 self.conn.commit()
#             else:
#                 return error.error_authorization_fail()
#         except sqlite.Error as e:
#             return 528, "{}".format(str(e))
#         except BaseException as e:
#             return 530, "{}".format(str(e))
#         return 200, "ok"
#
#     def change_password(
#         self, user_id: str, old_password: str, new_password: str
#     ) -> bool:
#         try:
#             code, message = self.check_password(user_id, old_password)
#             if code != 200:
#                 return code, message
#
#             terminal = "terminal_{}".format(str(time.time()))
#             token = jwt_encode(user_id, terminal)
#             cursor = self.conn.execute(
#                 "UPDATE user set password = ?, token= ? , terminal = ? where user_id = ?",
#                 (new_password, token, terminal, user_id),
#             )
#             if cursor.rowcount == 0:
#                 return error.error_authorization_fail()
#
#             self.conn.commit()
#         except sqlite.Error as e:
#             return 528, "{}".format(str(e))
#         except BaseException as e:
#             return 530, "{}".format(str(e))
#         return 200, "ok"


import jwt
import time
import logging
from pymongo import MongoClient
from be.model import error
from be.model import db_conn
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
            return error.error_exist_user_id(user_id)

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
            return error.error_authorization_fail()
        db_token = user.get("token")
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        user = self.db.users.find_one({"user_id": user_id})
        if user is None:
            return error.error_authorization_fail()
        db_password = user.get("password")
        if password != db_password:
            return error.error_authorization_fail()
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

    # def logout(self, user_id: str, token: str) -> bool:
    #     try:
    #         code, message = self.check_token(user_id, token)
    #         if code != 200:
    #             return code, message
    #
    #         terminal = "terminal_{}".format(str(time.time()))
    #         dummy_token = self.jwt_encode(user_id, terminal)
    #
    #         # 使用MongoDB的更新操作来更新用户记录
    #         update_result = self.db.users.update_one(
    #             {"user_id": user_id},
    #             {"$set": {"token": dummy_token, "terminal": terminal}}
    #         )
    #
    #         # 检查更新操作的结果
    #         if update_result.matched_count == 0:
    #             return 528, "未找到匹配的用户记录"
    #
    #     except Exception as e:
    #         return 530, "{}".format(str(e))
    #     return 200, "ok"

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



# user = User()
# # 指定用户的用户名和密码
# user_id = "user"
# password = "password"
# # 先注册用户
# code, message = user.login('user1', 'password1', 'terminal1')
#
# # 验证结果
# print(code)
# print(message)
#
#
# user = User()
#
# # Define user ID, password, and terminal
# user_id = "user1"
# password = "password1"
# terminal = "terminal1"
# token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcjEiLCJ0ZXJtaW5hbCI6InRlcm1pbmFsMSIsInRpbWVzdGFtcCI6MTY5ODI5NDY0NC44Nzk2OTY0fQ.1wBdTl7lckQs2-L_-BpixavBBQRt8m6SpDpcCmfUPhA'
#
# # login_code, login_message,token = user.login(user_id, password, terminal)
# # if login_code == 200:
# #     print("Login successful")
# #     print("Token:", token)
# # else:
# #     print("Login failed with code:", login_code)
# #     print("Message:", login_message)
#
# login_code, login_message = user.logout(user_id, token)
# if login_code == 200:
#     print("Logout successful")
#     print("Token:", token)
# else:
#     print("Logout failed with code:", login_code)
#     print("Message:", login_message)
#
# # user = User()
# # user_id = "test_user"
# # password = "test_password"
# # code, message = user.unregister(user_id, password)