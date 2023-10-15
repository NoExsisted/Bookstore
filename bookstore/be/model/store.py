# import logging
# import os
# import sqlite3 as sqlite
#
#
# class Store:
#     database: str
#
#     def __init__(self, db_path):
#         self.database = os.path.join(db_path, "be.db")
#         self.init_tables()
#
#     def init_tables(self):
#         try:
#             conn = self.get_db_conn()
#             conn.execute(
#                 "CREATE TABLE IF NOT EXISTS user ("
#                 "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
#                 "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
#             )
#
#             conn.execute(
#                 "CREATE TABLE IF NOT EXISTS user_store("
#                 "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
#             )
#
#             conn.execute(
#                 "CREATE TABLE IF NOT EXISTS store( "
#                 "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
#                 " PRIMARY KEY(store_id, book_id))"
#             )
#
#             conn.execute(
#                 "CREATE TABLE IF NOT EXISTS new_order( "
#                 "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
#             )
#
#             conn.execute(
#                 "CREATE TABLE IF NOT EXISTS new_order_detail( "
#                 "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
#                 "PRIMARY KEY(order_id, book_id))"
#             )
#
#             conn.commit()
#         except sqlite.Error as e:
#             logging.error(e)
#             conn.rollback()
#
#     def get_db_conn(self) -> sqlite.Connection:
#         return sqlite.connect(self.database)
#
#
# database_instance: Store = None
#
#
# def init_database(db_path):
#     global database_instance
#     database_instance = Store(db_path)
#
#
# def get_db_conn():
#     global database_instance
#     return database_instance.get_db_conn()
import logging
from pymongo import MongoClient


class Store:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']
        self.init_collections()

    def init_collections(self):
        # 初始化MongoDB集合，包括用户、用户商店、商店、新订单、新订单明细
        self.users = self.db["users"]
        self.user_stores = self.db["user_stores"]
        self.stores = self.db["stores"]
        self.new_orders = self.db["new_orders"]
        self.new_order_details = self.db["new_order_details"]

    def get_db_client(self) -> MongoClient:
        return self.client

    def init_tables(self):
        # 初始化MongoDB集合，定义数据模型，插入初始数据
        self.init_users_collection()
        self.init_user_stores_collection()
        self.init_stores_collection()
        self.init_new_orders_collection()
        self.init_new_order_details_collection()

    def init_users_collection(self):
        # 用户数据示例
        user_data = [
            {
                "user_id": "user1",
                "password": "password1",
                "balance": 100,
                "token": "",
                "terminal": "terminal1"
            },
            {
                "user_id": "user2",
                "password": "password2",
                "balance": 200,
                "token": "",
                "terminal": "terminal2"
            },
            # 添加更多用户数据
        ]

        self.users.insert_many(user_data)

    def init_user_stores_collection(self):
        # 初始化用户商店集合
        try:
            user_stores = self.db["user_stores"]
            user_stores.create_index([("user_id", 1), ("store_id", 1)], unique=True)  # 确保(user_id, store_id)是唯一的

            # 插入初始数据，根据需要定义和插入用户商店文档
            user_store_data = [
                {
                    "user_id": "user1",
                    "store_id": "store1"
                },
                {
                    "user_id": "user2",
                    "store_id": "store2"
                },
            ]

            user_stores.insert_many(user_store_data)
        except Exception as e:
            logging.error(e)

    def init_stores_collection(self):
        # 初始化商店集合，并添加初始数据
        store_data = [
            {
                "store_id": "store1",
                "book_info": "Book Info 1",
                "stock_level": 100,
                'id': "Book1",
                'title': "Book1",
                'author': "",
                'publisher': "",
                'original_title': "",
                'translator': "",
                'pub_year': "",
                'pages': "",
                'price': "",
                'binding': "",
                'isbn': "",
                'author_intro': "",
                'book_intro': "",
                'content': "",
                'tags': "",
                'picture': ""
            },
            # {
            #     "store_id": "store2",
            #     "book_id": "book2",
            #     "book_info": "Book Info 2",
            #     "stock_level": 50
            # },
        ]

        self.stores.insert_many(store_data)

    def init_new_orders_collection(self):
        # 初始化新订单集合
        try:
            new_orders = self.db["new_orders"]
            new_orders.create_index([("order_id", 1)], unique=True)  # 确保order_id是唯一的

            # 插入初始数据，根据需要定义和插入新订单文档
            new_order_data = [
                {
                    "order_id": "order1",
                    "user_id": "user1",
                    "store_id": "store1"
                },
                {
                    "order_id": "order2",
                    "user_id": "user2",
                    "store_id": "store2"
                },
            ]

            new_orders.insert_many(new_order_data)
        except Exception as e:
            logging.error(e)

    def init_new_order_details_collection(self):
        # 初始化新订单明细集合
        try:
            new_order_details = self.db["new_order_details"]
            new_order_details.create_index([("order_id", 1), ("book_id", 1)], unique=True)  # 确保(order_id, book_id)是唯一的

            # 插入初始数据，根据需要定义和插入新订单明细文档
            new_order_detail_data = [
                {
                    "order_id": "order1",
                    "book_id": "book1",
                    "count": 3,
                    "price": 50
                },
                {
                    "order_id": "order2",
                    "book_id": "book2",
                    "count": 2,
                    "price": 30
                },
            ]

            new_order_details.insert_many(new_order_detail_data)
        except Exception as e:
            logging.error(e)


database_instance: Store = None


def init_database(db_host, db_port, db_name):
    global database_instance
    database_instance = Store(db_host, db_port, db_name)
    database_instance.init_tables()


def get_db_client():
    global database_instance
    return database_instance.get_db_client()


# if __name__ == "__main__":
#     db_host = "localhost"
#     db_port = 27017
#     db_name = "bookstore"
#
#     init_database(db_host, db_port, db_name)
#
#     client = get_db_client()
