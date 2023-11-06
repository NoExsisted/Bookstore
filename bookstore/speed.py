from pymongo import MongoClient
import time

# 连接到MongoDB
client = MongoClient('localhost', 27017)
db = client['bookstore']

# 创建索引
db.users.create_index([("user_id", 1)])
db.books.create_index([("title", 1)])
db.stores.create_index([("store_id", 1)])

# store_dict = {
#     'store_id': 'store1',
#     'book_id': '1000121',
#     'book_info': {
#         'tags': [
#             '昆虫'
#         ],
#         'pictures': [],
#         'id': '1000121',
#         'title': '昆虫记',
#         'author': '[法] J·H·法布尔',
#         'publisher': '作家出版社',
#         'original_title': '',
#         'translator': '王光',
#         'pub_year': '2004-03',
#         'pages': 352,
#         'price': 1900,
#         'binding': '平装',
#         'isbn': '9787506312820',
#         'author_intro': '法布尔',
#         'book_intro': '《昆虫记》',
#         'content': '目录\n'
#     },
#     'stock_level': 10
# }
# db.stores.insert_one(store_dict)
#
# book_dict = {
#     'id': '3604517',
#     'title': '撒哈拉的故事',
#     'author': '三毛',
#     'publisher': '北京十月文艺出版社',
#     'original_title': '',
#     'translator': '',
#     'pub_year': '2009-3',
#     'pages': 294,
#     'price': 2000,
#     'currency_unit': '',
#     'binding': '平装',
#     'isbn': '9787530209653',
#     'author_intro': '三毛，台湾著名作家，1943年3月26日出生于重庆，浙江省定海县人。原名为陈懋平，1946年改名陈平，笔名“三毛”，英文名“Echo”。',
#     'book_intro': '收录散文19篇。记述三毛在撒哈拉沙漠的生活。这部散文集发表出版后，因其风趣自然的笔触、热情感恩的心灵和诚 挚悲悯的情怀，风靡全球万千的中文读者。\n',
#     'content': '',
#     'tags': '三毛\n撒哈拉的故事\n散文\n游记\n台湾\n生活\n中国文学\n文学\n',
#     'picture': ''
#   }
# db.books.insert_one(book_dict)
#
# user_dict = {
#     'user_id': '123456',
#     'password': '123456',
#     'balance': 12345,
#     'token': '123456',
#     'terminal': 'my terminal'
# }
# db.books.insert_one(user_dict)
#
# # 查询1 - 查询user文档
# query_user = {"user_id": '123456'}
#
# # 查询并测量时间（有索引）
# start_time = time.time()
# result_with_index_user = db.users.find(query_user)
# end_time = time.time()
# print(f"Time with index (user): {end_time - start_time} seconds")
#
# # 删除user索引
# db.users.drop_index([("user_id", 1)])
#
# # 查询并测量时间（无索引）
# start_time = time.time()
# result_without_index_user = db.users.find(query_user)
# end_time = time.time()
# print(f"Time without index (user): {end_time - start_time} seconds")
#
# # 查询2 - 查询book文档
# query_book = {"title": '撒哈拉的故事'}
#
# # 查询并测量时间（有索引）
# start_time = time.time()
# result_with_index_book = db.books.find(query_book)
# end_time = time.time()
# print(f"Time with index (book): {end_time - start_time} seconds")
#
# # 删除book索引
# db.books.drop_index([("title", 1)])
#
# # 查询并测量时间（无索引）
# start_time = time.time()
# result_without_index_book = db.books.find(query_book)
# end_time = time.time()
# print(f"Time without index (book): {end_time - start_time} seconds")
#
# # 查询3 - 查询store文档
# query_store = {"store_id": 'store1'}
#
# # 查询并测量时间（有索引）
# start_time = time.time()
# result_with_index_store = db.stores.find(query_store)
# end_time = time.time()
# print(f"Time with index (store): {end_time - start_time} seconds")
#
# # 删除store索引
# db.stores.drop_index([("store_id", 1)])
#
# # 查询并测量时间（无索引）
# start_time = time.time()
# result_without_index_store = db.stores.find(query_store)
# end_time = time.time()
# print(f"Time without index (store): {end_time - start_time} seconds")

# 关闭MongoDB连接
client.close()
