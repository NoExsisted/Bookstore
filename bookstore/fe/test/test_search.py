# import pytest
# from be.model.search import app
#
# # 为Flask应用程序定义一个测试客户端
# @pytest.fixture
# def client():
#     app.config['TESTING'] = True
#     with app.test_client() as client:
#         yield client
#
# def test_search_books_all(client):
#     response1 = client.get('/?search_query=book&search_scopes=title&search_scopes=tags&search_scopes=book_intro&search_scopes=content&store_search=&store_search_input=')
#     assert response1.status_code == 200
#
# def test_search_books_title(client):
#     response2 = client.get('/?search_query=book&search_scopes=title&store_search=&store_search_input=')
#     assert response2.status_code == 200
#
# def test_search_books_tags(client):
#     response3 = client.get('/?search_query=book&search_scopes=tags&&store_search=&store_search_input=')
#     assert response3.status_code == 200
#
# def test_search_books_intro(client):
#     response4 = client.get('/?search_query=book&search_scopes=book_intro&store_search=&store_search_input=')
#     assert response4.status_code == 200
#
# def test_search_content(client):
#     response4 = client.get('/?search_query=book&search_scopes=content&store_search=&store_search_input=')
#     assert response4.status_code == 200
#
# def test_pagination(client):
#     response6 = client.get('/?search_query=book&search_scopes=title&search_scopes=tags&search_scopes=book_intro&search_scopes=content&store_search=store&store_search_input=store')
#     assert response6.status_code == 200
#
# def test_pagination(client):
#     response6 = client.get('/?search_query=唐小卉&search_scopes=title&store_search=store&store_search_input=store1')
#     assert response6.status_code == 404
#
# if __name__ == '__main__':
#     pytest.main()



import uuid
import pytest
from fe.access import search_books
from fe import conf

class TestSearch:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.search = search_books.Search(conf.URL)

        self.search_query = "三毛"
        self.search_scopes = ["title"]
        self.store_name = "test_add_book_stock_level1_store_cca14d3d-77ab-11ee-bca9-900f0ce4b02c".format(str(uuid.uuid1()))

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
