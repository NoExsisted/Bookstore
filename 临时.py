# @app.route('/')
# def index():
#     page = int(request.args.get('page', 0))
#     search_query = request.args.get('search_query', '')
#     search_scopes = request.args.getlist('search_scopes')
#     store_search = request.args.get('store_search_input', '')
#     # 初始化结果列表
#     result_books = []
#     if store_search and request.args.get('store_search') == 'store':
#         # 如果用户选择了店铺搜索并且范围包括店铺
#         # 重新构建查询条件来查找符合店铺名字的店铺ID
#         stores = db.stores.find({'store_id': store_search})
#
#         for store in stores:
#             # 在每个店铺数据中查找符合搜索关键词的书本
#             store_id = store['store_id']
#             query = {
#                 '$and': [
#                     {'store_id': store_id},
#                     {
#                         '$or': []
#                     }
#                 ]
#             }
#
#             # 根据选择的搜索范围构建查询条件
#             if 'title' in search_scopes:
#                 query['$and'][1]['$or'].append({'title': {'$regex': search_query, '$options': 'i'}})
#
#             if 'tags' in search_scopes:
#                 query['$and'][1]['$or'].append({'tags': {'$in': [search_query]}})
#
#             if 'book_intro' in search_scopes:
#                 query['$and'][1]['$or'].append({'book_intro': {'$regex': search_query, '$options': 'i'}})
#
#             if 'content' in search_scopes:
#                 query['$and'][1]['$or'].append({'content': {'$regex': search_query, '$options': 'i'}})
#
#             # 如果用户没有选择任何搜索范围，将移除空的 '$or' 条件
#             if not query['$and'][1]['$or']:
#                 query['$and'].pop(1)
#             books = db.books.find(query)
#             result_books.extend(books)
#             total_results = len(result_books)
#             pagination = Pagination(page=page, total=total_results, search=False, per_page=RESULTS_PER_PAGE, css_framework='bootstrap4')
#             return render_template('index.html', books=result_books, pagination=pagination, search_query=search_query, search_scopes=search_scopes, store_search=store_search)
#     else:
#         # 如果不是店铺搜索，按照之前的逻辑进行普通搜索
#         books, total_results = get_books(page, search_query, search_scopes, store_search)
#         result_books.extend(books)
#
#     books, total_results = get_books(page, search_query, search_scopes, store_search)
#
#     pagination = Pagination(page=page, total=total_results, search=False, per_page=RESULTS_PER_PAGE, css_framework='bootstrap4')
#
#     return render_template('index.html', books=books, pagination=pagination, search_query=search_query, search_scopes=search_scopes, store_search=store_search)



# from flask import Flask, render_template, request
# from pymongo import MongoClient
#
# app = Flask(__name__)
#
# # MongoDB连接配置
# client = MongoClient('mongodb://localhost:27017/')
# db = client['bookstore']
#
# def get_books(search_query, search_scopes, store_search):
#     # 构建查询条件
#     query = {}
#     if search_query:
#         search_criteria = []
#
#         if 'title' in search_scopes:
#             search_criteria.append({'title': {'$regex': search_query, '$options': 'i'}})
#
#         if 'tags' in search_scopes:
#             search_criteria.append({'tags': {'$in': [search_query]}})
#
#         if 'book_intro' in search_scopes:
#             search_criteria.append({'book_intro': {'$regex': search_query, '$options': 'i'}})
#
#         if 'content' in search_scopes:
#             search_criteria.append({'content': {'$regex': search_query, '$options': 'i'}})
#
#         if search_criteria:
#             query['$or'] = search_criteria
#
#     if store_search:
#         query['store_id'] = store_search
#
#     # 获取总结果数
#     total_results = db.books.count_documents(query)
#
#     books = db.books.find(query)
#     return books, total_results
#
#
# # app.py
#
# # ...
#
# @app.route('/')
# def index():
#     page = int(request.args.get('page', 0))
#     search_query = request.args.get('search_query', '')
#     search_scopes = request.args.getlist('search_scopes')
#     store_search = request.args.get('store_search_input', '')
#
#     # 初始化结果列表
#     result_books = []
#
#     if store_search and request.args.get('store_search') == 'store':
#         # 如果用户选择了店铺搜索并且选择了 "Store" 选项
#         stores = db.stores.find({'store_id': store_search})
#
#         for store in stores:
#             # 在每个店铺数据中查找符合搜索关键词的书本
#             store_id = store['store_id']
#             query = {
#                 '$and': [
#                     {'store_id': store_id},
#                     {
#                         '$or': []
#                     }
#                 ]
#             }
#
#             # 根据选择的搜索范围构建查询条件
#             if 'title' in search_scopes:
#                 query['$and'][1]['$or'].append({'title': {'$regex': search_query, '$options': 'i'}})
#
#             if 'tags' in search_scopes:
#                 query['$and'][1]['$or'].append({'tags': {'$in': [search_query]}})
#
#             if 'book_intro' in search_scopes:
#                 query['$and'][1]['$or'].append({'book_intro': {'$regex': search_query, '$options': 'i'}})
#
#             if 'content' in search_scopes:
#                 query['$and'][1]['$or'].append({'content': {'$regex': search_query, '$options': 'i'}})
#
#             # 如果用户没有选择任何搜索范围，将移除空的 '$or' 条件
#             if not query['$and'][1]['$or']:
#                 query['$and'].pop(1)
#
#             books = db.stores.find(query)
#             result_books.extend(books)
#     else:
#         # 如果不是店铺搜索，按照之前的逻辑进行普通搜索
#         books, total_results = get_books(search_query, search_scopes, store_search)
#         result_books.extend(books)
#
#     total_results = len(result_books)
#     # print(total_results)
#     return render_template('index.html', books=result_books, search_query=search_query,
#                            search_scopes=search_scopes, store_search=store_search)
#
#
# if __name__ == '__main__':
#     app.run(debug=False)