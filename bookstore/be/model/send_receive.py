from be.model import error
from pymongo import MongoClient


class SendAndReceive:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']

    def send_books(self, user_id: str, order_id: str):
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

    def receive_books(self, user_id: str, order_id: str) -> (int, str):
        result = self.db.new_order_paid.find_one({"order_id": order_id})
        if result is None:
            return error.error_invalid_order_id(order_id)

        buyer_id = result["user_id"]
        books_status = result["books_status"]

        if buyer_id != user_id:
            return error.error_authorization_fail()
        if books_status == 1:
            return error.error_book_has_not_sent()
        if books_status == 2:
            return error.error_not_paid_book()

        self.db.new_order_paid.update_one({"order_id": order_id}, {"$set": {"books_status": 3}})

        return 200, "ok"

