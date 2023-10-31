import sqlite3 as sqlite
import json
from be.model import error
from be.model import db_conn
from pymongo import MongoClient


class Seller(db_conn.DBConn):
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']
        #db_conn.DBConn.__init__(self)

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
                "book_info":  json.loads(book_json_str),
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

            '''self.conn.execute(
                "UPDATE store SET stock_level = stock_level + ? "
                "WHERE store_id = ? AND book_id = ?",
                (add_stock_level, store_id, book_id),
            )
            self.conn.commit()'''


            #condition = {"store_id": store_id, "book_id": book_id}
            self.db.stores.update_one(
                {"store_id": store_id, "book_id": book_id},
                {"$inc": {"stock_level": add_stock_level}}
            )
            #self.db.stores.update_many(condition, {'$inc': {'stock_level': +add_stock_level}})
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
            '''self.conn.execute(
                "INSERT into user_store(store_id, user_id)" "VALUES (?, ?)",
                (store_id, user_id),
            )
            self.conn.commit()'''
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
