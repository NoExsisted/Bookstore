import uuid
import logging
from be.model import db_conn
from be.model import error
from pymongo import MongoClient
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler


class Buyer(db_conn.DBConn):
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            # 查询用户是否存在，不存在返回错误
            user = self.db.users.find_one({"user_id": user_id})
            if user is None:
                return error.error_non_exist_user_id(user_id) + (order_id,)

            store = self.db.stores.find_one({"store_id": store_id})
            if store is None:
                return error.error_non_exist_store_id(user_id) + (order_id,)

            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                result = self.db.stores.find_one({"store_id": store_id, "book_id": book_id})
                if result is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = result["stock_level"]
                book_info = result["book_info"]
                price = book_info["price"]
                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                condition = {"store_id": store_id, "book_id": book_id, "stock_level": {'$gte': count}}
                self.db.stores.update_one(condition,{"$inc": {"stock_level": -1}})

                new_order_detail = {
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price,
                    "books_status": 2
                }
                self.db.new_order_details.insert_one(new_order_detail)

            now_time = datetime.utcnow()
            new_order = {
                "order_id": uid,
                "user_id": user_id,
                "store_id": store_id,
                "books_status": 2,
                "order_time": now_time,
            }
            print(new_order)
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
            
            order_id = result["order_id"]
            buyer_id = result["user_id"]
            store_id = result["store_id"]

            if buyer_id != user_id:
                return error.error_authorization_fail()
            
            result = self.db.users.find_one({"user_id": buyer_id})
            if result is None:
                return error.error_non_exist_user_id(buyer_id)

            balance = result["balance"]
            if password != result["password"]:
                return error.error_authorization_fail()

            result = self.db.user_stores.find_one({"store_id": store_id})
            if result is None:
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
            self.db.users.update_many(condition, {"$inc": {"balance": -total_price}})

            condition = {"user_id": seller_id}
            self.db.users.update_many(condition, {"$inc": {"balance": +total_price}})
            # condition只有id，所以可以先改再查
            row = self.db.users.count_documents(condition)

            if row == 0:
                return error.error_non_exist_user_id(buyer_id)
            # 已经付款的会从order的两个表里面删除掉

            row = self.db.new_orders.count_documents({"order_id": order_id})
            self.db.new_orders.delete_many({"order_id": order_id})

            if row == 0:
                return error.error_invalid_order_id(order_id)
            
            row = self.db.new_order_details.count_documents({"order_id": order_id})
            self.db.new_order_details.delete_many({"order_id": order_id})
            if row == 0:
                return error.error_invalid_order_id(order_id)
            new_order_paid = {
                "order_id": order_id,
                "user_id": buyer_id,
                "store_id": store_id,
                "books_status": 1,  # 1：已支付下单没发货
                "price": total_price
            }
            self.db.new_order_paid.insert_one(new_order_paid)

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
            self.db.users.update_one(condition, {"$inc": {"balance": +add_value}})

        except Exception as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

#
#     # 订单取消 增加余额 增加库存
#     def new_order_cancel(self, user_id: str, order_id: str) -> (int, str):
#         store_id = ""
#         price = ""
#         new_order = self.db.new_orders.find_one({"order_id": order_id})
#         # 未支付订单取消：手动取消\自动取消
#         # 手动取消
#         if new_order is not None:
#             buyer_id = new_order["user_id"]
#             if buyer_id != user_id:
#                 return error.error_authorization_fail()
#
#             self.db.new_orders.delete_one({"order_id": order_id})
#
#         # 如果已经支付的话需要取消订单以后减少商家余额，增加用户余额
#         else:
#             new_order_paid = self.db.new_order_paid.find_one({"order_id": order_id})
#             if new_order_paid:
#                 buyer_id = new_order_paid["user_id"]
#
#                 if buyer_id != user_id:
#                     return error.error_authorization_fail()
#                 # 找到对应商店和价格
#                 store_id = new_order_paid["store_id"]
#                 price = new_order_paid["price"]
#
#                 # 根据商店找到卖家
#                 user_store = self.db.user_stores.find_one({"store_id": store_id})
#                 if user_store is None:
#                     return error.error_non_exist_store_id(store_id)
#                 seller_id = user_store["user_id"]
#
#                 # 减少卖家余额
#                 condition = {"$inc": {"balance": -price}}
#                 seller = {"user_id": seller_id}
#                 result = self.db.users.update_one(seller, condition)
#                 if result is None:
#                     return error.error_non_exist_user_id(seller_id)
#
#                 # 增加买家余额
#                 buyer = {"user_id": buyer_id}
#                 condition = {"$inc": {"balance": price}}
#                 result = self.db.used.update_one(buyer, condition)
#                 if result is None:
#                     return error.error_non_exist_user_id(user_id)
#
#                 # 删除订单
#                 result = self.db.new_order_paid.delete_one({"order_id": order_id})
#                 if result is None:
#                     return error.error_invalid_order_id(order_id)
#
#             else:
#                 return error.error_invalid_order_id(order_id)
#
#             # 增加书籍库存
#         orders = self.db.new_order_details.find({"order_id": order_id})
#         for order in orders:
#             book_id = order["book_id"]
#             count = order["count"]
#             store_book = {"store_id": store_id, "book_id": book_id}
#             condition = {"$inc": {"stock_level": count}}
#             result = self.db.stores.update_one(store_book, condition)
#
#         return 200, "ok"
#
#     # 查询历史订单
#     def check_order(self, user_id: str):
#         # 最后返回一个订单详情
#         his_order_detail = []
#
#         user = self.db.users.find_one({"user_id": user_id})
#         if user is None:
#             return error.error_non_exist_user_id(user_id)
#
#         # 查询历史订单分为：查询未付款的订单、查询已经付款的订单
#         # 查询未付款订单
#         user = {"user_id": user_id}
#         new_orders = self.db.new_order_details.find(user)
#         if new_orders:
#             book_id = ""
#             count = ""
#             price = ""
#             status = ""
#
#             for new_order in new_orders:
#                 order_id = new_order["order_id"]
#                 order = {"order_id": order_id}
#                 new_order_details = self.db.new_order_details.find(order)
#
#                 if new_order_details:
#                     for new_order_detail in new_order_details:
#                         # 保存书的详细信息
#                         book_id = new_order_detail["book_id"]
#                         count = new_order_detail["count"]
#                         price = new_order_detail["price"]
#                         status = new_order_detail["books_status"]
#
#                 else:
#                     return error.error_invalid_order_id(order_id)
#
#                 details = {
#                     "status": status,
#                     "order_id": order_id,
#                     "buyer_id": new_order["user_id"],
#                     "store_id": new_order["store_id"],
#                     "price": price,
#                     "book_id": book_id,
#                     "count": count,
#                 }
#
#                 his_order_detail.append(details)
#
#
#         # 查询已付款订单
#         new_orders_paid = self.db.new_order_paid.find(user)
#
#         if new_orders_paid:
#             book_id = ""
#             count = ""
#             price = ""
#             status = ""
#             for new_order_paid in new_orders_paid:
#                 order_id = new_order_paid["order_id"]
#                 order = {"order_id": order_id}
#                 new_order_details = self.db.new_order_details.find(order)
#                 if new_order_details:
#                     for new_order_detail in new_order_details:
#                         # 保存书的详细信息
#                         book_id = new_order_detail["book_id"]
#                         count = new_order_detail["count"]
#                         price = new_order_detail["price"]
#                         status = new_order_detail["books_status"]
#
#                 else:
#                     return error.error_invalid_order_id(order_id)
#
#                 details = {
#                     "status": status,
#                     "order_id": order_id,
#                     "buyer_id": new_order_paid["user_id"],
#                     "store_id": new_order_paid["store_id"],
#                     "total_price": new_order_paid["price"],
#                     "price": price,
#                     "book_id": book_id,
#                     "count": count,
#                 }
#                 his_order_detail.append(details)
#
#         return 200, "ok"
#
#     def timeout_cancel(self, order_id: str):
#         self.db.new_orders.delete_one({"order_id": order_id})
#         return 200, "ok"
#
#     def check_order_status(self):
#         timeout_datetime = datetime.now() - timedelta(seconds = 5)
#         condition = {"order_time": {"$lte": timeout_datetime}} # 表示小于超时时间戳都应该被取消
#         orders = self.db.new_orders.find(condition)
#         if orders is not None:
#             for order in orders:
#
#                 order_id = order["order_id"]
#                 self.db.new_orders.delete_one({"order_id": order_id})
#
#         return 200, "ok"
#
#
# b = Buyer()
# scheduler = BackgroundScheduler()
# scheduler.add_job(b.check_order_status, 'interval',  seconds=5)
# scheduler.start()





    # def receive_books(self, user_id: str, order_id: str) -> (int, str):
    #     result = self.db.new_order_paid.find_one({"order_id": order_id})
    #     if result is None:
    #         return error.error_invalid_order_id(order_id)
    #
    #     buyer_id = result["user_id"]
    #     books_status = result["books_status"]
    #
    #     if buyer_id != user_id:
    #         return error.error_authorization_fail()
    #     if books_status == 1:
    #         return error.error_book_has_not_sent()
    #     if books_status == 2:
    #         return error.error_not_paid_book()
    #     if books_status == 3:
    #         return error.error_book_has_received()
    #     self.db.new_order_paid.update_one({"order_id": order_id}, {"$set": {"books_status": 3}})
    #
    #     return 200, "ok"







