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
                return error.error_non_exist_store_id(user_id) + (order_id,)
            #if not self.store_id_exist(store_id):
            #    return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                result = self.db.stores.find_one({"store_id": store_id, "book_id": book_id})
                if result is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)
                #row = self.db.stores.count_documents({"store_id": store_id, "book_id": book_id})
                #if row == 0:
                #    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = result["stock_level"]
                book_info = result["book_info"]
                price = book_info["price"]
                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                condition = {"store_id": store_id, "book_id": book_id, "stock_level": {'$gte': count}}
                row = self.db.stores.count_documents(condition)
                if row == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                result = self.db.stores.update_one(
                    condition,
                    {"$inc": {"stock_level": -1}}
                )

                #if result.modified_count == 0:
                #    return error.error_stock_level_low(book_id) + (order_id,)



                #condition = {"store_id": store_id, "book_id": book_id, "stock_level": {'$gte': count}}
                #row = self.db.stores.count_documents(condition)
                #if row == 0:
                #    return error.error_stock_level_low(book_id) + (order_id,)
                
                #self.db.stores.update_many(condition, {'$inc': {'stock_level': -count}})

                new_order_detail = {
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                }
                self.db.new_order_details.insert_one(new_order_detail)

            new_order = {
                "order_id": uid,
                "user_id": user_id,
                "store_id": store_id
            }
            self.db.new_orders.insert_one(new_order)
            order_id = uid
        except Exception as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""

        return 200, "ok", order_id
    
    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            result = self.db.new_orders.find_one({"order_id": order_id})
            if result is None:
                return error.error_invalid_order_id(order_id)

            #row = self.db.new_orders.count_documents({"order_id": order_id})
            #if row == 0:
            #    return error.error_invalid_order_id(order_id)
            
            order_id = result["order_id"]
            buyer_id = result["user_id"]
            store_id = result["store_id"]

            if buyer_id != user_id:
                return error.error_authorization_fail()
            
            result = self.db.users.find_one({"user_id": buyer_id})
            if result is None:
                return error.error_non_exist_user_id(buyer_id)

            #row = self.db.users.count_documents({"user_id": buyer_id})
            #if row == 0:
            #    return error.error_non_exist_user_id(buyer_id)
            
            balance = result["balance"]
            if password != result["password"]:
                return error.error_authorization_fail()

            result = self.db.user_stores.find_one({"store_id": store_id})
            if result is None:
                return error.error_non_exist_store_id(store_id)

            #row = self.db.user_stores.count_documents({"store_id": store_id})
            #if row == 0:
            #    return error.error_non_exist_store_id(store_id)
            
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

            condition = {"user_id": seller_id}
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
'''
    ## 订单取消
    def new_order_cancel(self, user_id: str, order_id: str) ->(int, str):
        new_order = self.db.new_orders.find_one({"order_id": order_id})
        if new_order:

            buyer_id = new_order["user_id"]
            if buyer_id != user_id:
                return error.error_authorization_fail()

            self.db.new_orders.delete_one({"order_id": order_id})

        # 如果已经支付的话需要取消订单以后减少商家余额，增加用户余额，增加商店该书籍库存
        else:
            new_order_paid = self.db.new_order_paid.find_one({"order_id": order_id})
            if new_order_paid:
                buyer_id = new_order_paid["user_id"]

                if buyer_id != user_id:
                    return error.error_authorization_fail()
                # 找到对应商店和价格
                store_id = new_order_paid["store_id"]
                price = new_order_paid["price"]

                # 根据商店找到卖家
                user_store = self.db.user_stores.find_one({"store_id": store_id})
                if user_store is None:
                    return error.error_non_exist_store_id(store_id)
                seller_id = user_store["user_id"]

                # 减少卖家余额
                condition = {"$inc": {"balance": -price}}
                seller = {"user_id": seller_id}
                result = self.db.users.update_one(seller, condition)
                if result is None:
                    return error.error_non_exist_user_id(seller_id)

                # 增加买家余额
                buyer = {"user_id": buyer_id}
                condition = {"$inc": {"balance": price}}
                result = self.db.used.update_one(buyer, condition)
                if result is None:
                    return error.error_non_exist_user_id(user_id)

                # 删除订单
                result = self.db.new_order_paid.delete_one(order_query)
                if delete_result is None:
                    return error.error_invalid_order_id(order_id)

            else:
                return error.error_invalid_order_id(order_id)

            # increase the stock level depending on the order detail
        book_doc = self.conn.new_order_detail_collection.find(order_query)
        for book in book_doc:
            book_id = book["book_id"]
            count = book["count"]
            query = {"store_id": store_id, "book_id": book_id}
            update = {"$inc": {"stock_level": count}}
            update_result = self.conn.store_collection.update_one(query, update)
            if update_result.modified_count == 0:
                return error.error_stock_level_low(book_id) + (order_id,)

        # insert this cancelled order into new_order_cancel
        insert_order = {"order_id": order_id, "user_id": user_id, "store_id": store_id, "price": price}
        self.conn.new_order_cancel_collection.insert_one(insert_order)
        return 200, "ok"
'''



