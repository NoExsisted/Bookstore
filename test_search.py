import pytest
from app import app

# 为Flask应用程序定义一个测试客户端
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_search_books_all(client):
    response1 = client.get('/?search_query=book&search_scopes=title&search_scopes=tags&search_scopes=book_intro&search_scopes=content&store_search=&store_search_input=')
    assert response1.status_code == 200

def test_search_books_title(client):
    response2 = client.get('/?search_query=book&search_scopes=title&store_search=&store_search_input=')
    assert response2.status_code == 200

def test_search_books_tags(client):
    response3 = client.get('/?search_query=book&search_scopes=book_intro&store_search=&store_search_input=')
    assert response3.status_code == 200

def test_search_books_intro(client):
    response4 = client.get('/?search_query=book&search_scopes=tags&store_search=&store_search_input=')
    assert response4.status_code == 200

def test_search_content(client):
    response4 = client.get('/?search_query=book&search_scopes=content&store_search=&store_search_input=')
    assert response4.status_code == 200

def test_pagination(client):
    response6 = client.get('/?search_query=book&search_scopes=title&search_scopes=tags&search_scopes=book_intro&search_scopes=content&store_search=store&store_search_input=store')
    assert response6.status_code == 200

if __name__ == '__main__':
    pytest.main()
