import uuid
import logging
from be.model import db_conn
from be.model import error
from pymongo import MongoClient
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler


class Order:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']

    # 订单取消 增加余额 增加库存
    def new_order_cancel(self, user_id: str, order_id: str) -> (int, str):
        store_id = ""
        price = ""
        new_order = self.db.new_orders.find_one({"order_id": order_id})
        # 未支付订单取消：手动取消\自动取消
        # 手动取消
        if new_order is not None:
            buyer_id = new_order["user_id"]
            if buyer_id != user_id:
                return error.error_authorization_fail()

            self.db.new_orders.delete_one({"order_id": order_id})

        # 如果已经支付的话需要取消订单以后减少商家余额，增加用户余额
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

                seller_id = user_store["user_id"]

                # 减少卖家余额
                condition = {"$inc": {"balance": -price}}
                seller = {"user_id": seller_id}
                self.db.users.update_one(seller, condition)

                # 增加买家余额
                buyer = {"user_id": buyer_id}
                condition = {"$inc": {"balance": price}}
                self.db.used.update_one(buyer, condition)

                # 删除订单
                self.db.new_order_paid.delete_one({"order_id": order_id})

            else:
                return error.error_invalid_order_id(order_id)

            # 增加书籍库存
        orders = self.db.new_order_details.find({"order_id": order_id})
        for order in orders:
            book_id = order["book_id"]
            count = order["count"]
            store_book = {"store_id": store_id, "book_id": book_id}
            condition = {"$inc": {"stock_level": count}}
            result = self.db.stores.update_one(store_book, condition)

        return 200, "ok"

    # 查询历史订单
    def check_order(self, user_id: str):
        # 最后返回一个订单详情
        # his_order_detail = []

        user = self.db.users.find_one({"user_id": user_id})
        if user is None:
            return error.error_non_exist_user_id(user_id)

        # 查询历史订单分为：查询未付款的订单、查询已经付款的订单
        # 查询未付款订单
        user = {"user_id": user_id}
        new_orders = self.db.new_order_details.find(user)
        if new_orders:
            # book_id = ""
            # count = ""
            # price = ""
            # status = ""

            for new_order in new_orders:
                order_id = new_order["order_id"]
                order = {"order_id": order_id}
                new_order_details = self.db.new_order_details.find(order)

                if new_order_details is None:
                    # for new_order_detail in new_order_details:
                    #     # 保存书的详细信息
                    #     book_id = new_order_detail["book_id"]
                    #     count = new_order_detail["count"]
                    #     price = new_order_detail["price"]
                    #     status = new_order_detail["books_status"]

                    return error.error_invalid_order_id(order_id)

                # details = {
                #     "status": status,
                #     "order_id": order_id,
                #     "buyer_id": new_order["user_id"],
                #     "store_id": new_order["store_id"],
                #     "price": price,
                #     "book_id": book_id,
                #     "count": count,
                # }

                # his_order_detail.append(details)


        # 查询已付款订单
        new_orders_paid = self.db.new_order_paid.find(user)

        if new_orders_paid:
            # book_id = ""
            # count = ""
            # price = ""
            # status = ""
            for new_order_paid in new_orders_paid:
                order_id = new_order_paid["order_id"]
                order = {"order_id": order_id}
                new_order_details = self.db.new_order_details.find(order)
                if new_order_details is None:
                    # for new_order_detail in new_order_details:
                        # 保存书的详细信息
                        # book_id = new_order_detail["book_id"]
                        # count = new_order_detail["count"]
                        # price = new_order_detail["price"]
                        # status = new_order_detail["books_status"]


                    return error.error_invalid_order_id(order_id)

                # details = {
                #     "status": status,
                #     "order_id": order_id,
                #     "buyer_id": new_order_paid["user_id"],
                #     "store_id": new_order_paid["store_id"],
                #     "total_price": new_order_paid["price"],
                #     "price": price,
                #     "book_id": book_id,
                #     "count": count,
                # }
                # his_order_detail.append(details)

        return 200, "ok"

    def check_order_status(self):
        timeout_datetime = datetime.now() - timedelta(seconds = 5)
        condition = {"order_time": {"$lte": timeout_datetime}} # 表示小于超时时间戳都应该被取消
        orders = self.db.new_orders.find(condition)
        if orders is not None:
            for order in orders:
                order_id = order["order_id"]
                self.db.new_orders.delete_one({"order_id": order_id})

        return 200, "ok"


b = Order()
scheduler = BackgroundScheduler()
scheduler.add_job(b.check_order_status, 'interval',  seconds=5)
scheduler.start()