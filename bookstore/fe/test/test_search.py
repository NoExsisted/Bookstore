import uuid
import pytest
from fe.access import search_books
import pymongo
from fe import conf

client = pymongo.MongoClient('localhost', 27017)
db = client['bookstore']
book_dict = {
    'id': 'book',
    'title': '昆虫记',
    'author': 'book',
    'publisher': 'book',
    'original_title': 'book',
    'translator': 'book',
    'pub_year': 'book',
    'pages': 'book',
    'price': 'book',
    'binding': 'book',
    'isbn': 'book',
    'author_intro': 'book',
    'book_intro': 'book',
    'content': 'book',
    'tags': 'book',
    'picture': []
}
db.books.insert_one(book_dict)

store_dict = {
    'store_id': 'store1',
    'book_id': '1000121',
    'book_info': {
        'tags': [
            '昆虫'
        ],
        'pictures': [],
        'id': '1000121',
        'title': '昆虫记',
        'author': '[法] J·H·法布尔',
        'publisher': '作家出版社',
        'original_title': '',
        'translator': '王光',
        'pub_year': '2004-03',
        'pages': 352,
        'price': 1900,
        'binding': '平装',
        'isbn': '9787506312820',
        'author_intro': '法布尔',
        'book_intro': '《昆虫记》',
        'content': '目录\n'
    },
    'stock_level': 10
}
db.stores.insert_one(store_dict)

class TestSearch:

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.search = search_books.Search(conf.URL)
        self.search_query = "昆虫"
        self.search_scopes = ["title", "tags", "content", "book_intro"]
        self.store_name = "store1".format(str(uuid.uuid1()))

    def test_search_books(self):
        status, result = self.search.books(self.search_query, self.search_scopes)
        assert status == 200

    def test_search_books_wrong(self):
        status, result = self.search.books('txh', self.search_scopes)
        assert status == 404

    def test_search_stores(self):
        status, result = self.search.stores(self.store_name, self.search_query, self.search_scopes)
        assert status == 200

    def test_search_stores_wrong(self):
        status, result = self.search.stores('store111', self.search_query, self.search_scopes)
        assert status == 404

    def test_search_stores_nonexistent_store_id(self):
        status, result = self.search.stores('non_existent_store_id', self.search_query, self.search_scopes)
        assert status == 404

    def test_search_books_no_scope(self):
        search_query = "昆虫"
        search_scopes = []
        status, result = self.search.books(search_query, search_scopes)
        assert status == 200

    def test_search_books_no_query_and_scope(self):
        search_query = ""
        search_scopes = []
        status, result = self.search.books(search_query, search_scopes)
        assert status == 200

    def test_search_books_single_scope_no_match(self):
        search_query = "txh"
        search_scopes = ["title"]
        status, result = self.search.books(search_query, search_scopes)
        assert status == 404

    def test_search_books_multiple_scopes_no_match(self):
        search_query = "txh"
        search_scopes = ["title", "tags", "content"]
        status, result = self.search.books(search_query, search_scopes)
        assert status == 404


    def test_search_stores_single_store_no_match(self):
        store_name = "store1"
        search_query = "txh"
        search_scopes = ["title"]
        status, result = self.search.stores(store_name, search_query, search_scopes)
        assert status == 404


    def test_search_stores_multiple_stores_no_match(self):
        store_name = "store1"
        search_query = "txh"
        search_scopes = ["title", "tags", "content"]
        status, result = self.search.stores(store_name, search_query, search_scopes)
        assert status == 404



