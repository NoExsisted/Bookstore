# from be.model import store
#
#
# class DBConn:
#     def __init__(self):
#         self.conn = store.get_db_conn()
#
#     def user_id_exist(self, user_id):
#         cursor = self.conn.execute(
#             "SELECT user_id FROM user WHERE user_id = ?;", (user_id,)
#         )
#         row = cursor.fetchone()
#         if row is None:
#             return False
#         else:
#             return True
#
#     def book_id_exist(self, store_id, book_id):
#         cursor = self.conn.execute(
#             "SELECT book_id FROM store WHERE store_id = ? AND book_id = ?;",
#             (store_id, book_id),
#         )
#         row = cursor.fetchone()
#         if row is None:
#             return False
#         else:
#             return True
#
#     def store_id_exist(self, store_id):
#         cursor = self.conn.execute(
#             "SELECT store_id FROM user_store WHERE store_id = ?;", (store_id,)
#         )
#         row = cursor.fetchone()
#         if row is None:
#             return False
#         else:
#             return True


from pymongo import MongoClient
from be.model import store


class DBConn:
    def __init__(self):
        # self.conn = store.get_db_client()
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']

    def user_id_exist(self, user_id):
        users = self.db["users"]
        user = users.find_one({"user_id": user_id})
        return user is not None

    def book_id_exist(self, store_id, book_id):
        stores = self.db["stores"]
        store = stores.find_one({"store_id": store_id, "book_id": book_id})
        return store is not None

    def store_id_exist(self, store_id):
        user_stores = self.db["user_stores"]
        user_store = user_stores.find_one({"store_id": store_id})
        return user_store is not None