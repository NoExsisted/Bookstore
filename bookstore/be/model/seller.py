import json
from be.model import error
from be.model import db_conn
from pymongo import MongoClient


class Seller(db_conn.DBConn):
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']
        # db_conn.DBConn.__init__(self)

    def add_book(
            self,
            user_id: str,
            store_id: str,
            book_id: str,
            book_json_str: str,
            stock_level: int,
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            '''self.conn.execute(
                "INSERT into store(store_id, book_id, book_info, stock_level)"
                "VALUES (?, ?, ?, ?)",
                (store_id, book_id, book_json_str, stock_level),
            )
            self.conn.commit()'''
            store_entry = {
                "store_id": store_id,
                "book_id": book_id,
                "book_info": json.loads(book_json_str),
                "stock_level": stock_level
            }
            self.db.stores.insert_one(store_entry)
        except Exception as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
            self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            # condition = {"store_id": store_id, "book_id": book_id}
            self.db.stores.update_one(
                {"store_id": store_id, "book_id": book_id},
                {"$inc": {"stock_level": add_stock_level}}
            )
            # self.db.stores.update_many(condition, {'$inc': {'stock_level': +add_stock_level}})
        except Exception as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            user_store_entry = {
                "store_id": store_id,
                "user_id": user_id
            }
            self.db.user_stores.insert_one(user_store_entry)

        except Exception as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"


'''
    def send_books(self, user_id: str, order_id: str) -> (int, str):
        result = self.db.new_order_paid.find_one({"order_id": order_id})
        if result is None:
            return error.error_invalid_order_id(order_id)

        store_id = result["store_id"]
        books_status = result["books_status"]

        # 根据 store_id 找卖家
        result = self.db.user_stores.find_one({"store_id": store_id})
        seller_id = result["user_id"]

        if seller_id != user_id:
            return error.error_authorization_fail()

        if books_status == 0:
            return error.error_book_has_sent()

        if books_status == 2:
            return error.error_not_paid_book()

        if books_status == 3:
            return error.error_book_has_received()

        self.db.new_order_paid.update_one({"order_id": order_id}, {"$set": {"books_status": 0}})

        return 200, "ok"
'''