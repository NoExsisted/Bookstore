import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from pymongo import MongoClient


class Buyer(db_conn.DBConn):
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']
        #db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            # 查询用户是否存在，不存在返回错误
            user = self.db.users.find_one({"user_id": user_id})
            if user is None:
                return error.error_non_exist_user_id(user_id) + (order_id,)
            #if not self.user_id_exist(user_id):
            #    return error.error_non_exist_user_id(user_id) + (order_id,)

            store = self.db.stores.find_one({"store_id": store_id})
            if store is None:
                return error.error_non_exist_user_id(user_id) + (order_id,)
            #if not self.store_id_exist(store_id):
            #    return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                result = self.db.stores.find_one({"store_id": store_id, "book_id": book_id})
                row = self.db.stores.count_documents({"store_id": store_id, "book_id": book_id})
                if row == 0:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = result["stock_level"]
                price = result["price"]
                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)
                
                condition = {"store_id": store_id, "book_id": book_id, "stock_level": {'$gte': count}}
                row = self.db.stores.count_documents(condition)
                if row == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)
                
                self.db.stores.update_many(condition, {'$inc': {'$stock_level': -1}})

                new_order_detail = {
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                }
                self.db.new_order_details.insert_one(new_order_detail)
                order_id = uid
        except Exception as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""

        return 200, "ok", order_id
    
    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            result = self.db.new_orders.find_one({"order_id": order_id})
            row = self.db.new_orders.count_documents({"order_id": order_id})
            if row == 0:
                return error.error_invalid_order_id(order_id)
            
            order_id = result["order_id"]
            buyer_id = result["user_id"]
            store_id = result["store_id"]

            if buyer_id != user_id:
                return error.error_authorization_fail()
            
            result = self.db.users.find_one({"user_id": buyer_id})
            row = self.db.users.count_documents({"user_id": buyer_id})
            if row == 0:
                return error.error_non_exist_user_id(buyer_id)
            
            balance = result["balance"]
            if password != result["password"]:
                return error.error_authorization_fail()

            result = self.db.user_stores.find_one({"store_id": store_id})
            row = self.db.user_stores.count_documents({"store_id": store_id})
            if row == 0:
                return error.error_non_exist_store_id(store_id)
            
            seller_id = result["user_id"]
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            result = self.db.new_order_details.find({"order_id": order_id})
            total_price = 0
            for each in result:
                count = each["count"]
                price = each["price"]
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)
            
            condition = {"user_id": buyer_id, "balance": {"$gte": total_price}}
            row = self.db.users.count_documents(condition)
            if row == 0:
                return error.error_not_sufficient_funds(order_id)
            # 先找到符合条件的再改，不然变了
            result = self.db.users.update_many(condition, {"$inc": {"balance": -total_price}})

            condition = {"user_id": buyer_id}
            result = self.db.users.update_many(condition, {"$inc": {"balance": +total_price}})
            # condition只有id，所以可以先改再查
            row = self.db.users.count_documents(condition)

            if row == 0:
                return error.error_non_exist_user_id(buyer_id)
            
            row = self.db.new_orders.count_documents({"order_id": order_id})
            result = self.db.new_orders.delete_many({"order_id": order_id})
            if row == 0:
                return error.error_invalid_order_id(order_id)
            
            row = self.db.new_order_details.count_documents({"order_id": order_id})
            result = self.db.new_order_details.delete_many({"order_id": order_id})
            if row == 0:
                return error.error_invalid_order_id(order_id)
            pass
        except Exception as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
    
    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            result = self.db.users.find_one({"user_id": user_id})
            row = self.db.users.count_documents({"user_id": user_id})
            if row == 0:
                return error.error_authorization_fail()
            
            if result["password"] != password:
                return error.error_authorization_fail()
            
            condition = {"user_id": user_id}
            row = self.db.users.count_documents(condition)
            if row == 0:
                return error.error_non_exist_user_id(user_id)
            result = self.db.users.update_one(condition, {"$inc": {"balance": +add_value}})

        except Exception as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
