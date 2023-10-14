import pymongo
import os
import sqlite3 as sqlite
from pymongo import MongoClient

class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []

class BookDB:
    def __init__(self):
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.book_db = "book_lx.db"

    def get_all_books(self):
        conn = sqlite.connect(self.book_db)
        cursor = conn.execute(
            "SELECT id, title, author, publisher, original_title, translator, pub_year, pages, price, "
            "binding, isbn, author_intro, book_intro, content, tags, picture FROM book"
        )

        books = []
        for row in cursor:
            book = Book()
            book.id = row[0]
            book.title = row[1]
            book.author = row[2]
            book.publisher = row[3]
            book.original_title = row[4]
            book.translator = row[5]
            book.pub_year = row[6]
            book.pages = row[7]
            book.price = row[8]
            book.binding = row[9]
            book.isbn = row[10]
            book.author_intro = row[11]
            book.book_intro = row[12]
            book.content = row[13]
            tags = row[14]
            picture = row[15]

            for tag in tags.split("\n"):
                if tag.strip() != "":
                    book.tags.append(tag)

            books.append(book)

        return books

client_mongodb = MongoClient('localhost', 27017)
db_mongodb = client_mongodb['bookstore']
collection_mongodb = db_mongodb['books']

def init_mongodb():
    # 连接到MongoDB数据库
    client = pymongo.MongoClient('localhost', 27017) 
    db = client["bookstore"]  # 数据库名称

    # 创建用户集合并添加索引
    users = db["users"]
    users.create_index("user_id", unique=True)

if __name__ == "__main__":
    init_mongodb()
    book_database = BookDB()

    all_books = book_database.get_all_books()

    for book in all_books:
        book_dict = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'publisher': book.publisher,
            'original_title': book.original_title,
            'translator': book.translator,
            'pub_year': book.pub_year,
            'pages': book.pages,
            'price': book.price,
            'binding': book.binding,
            'isbn': book.isbn,
            'author_intro': book.author_intro,
            'book_intro': book.book_intro,
            'content': book.content,
            'tags': book.tags,
            'picture': book.pictures
        }

        collection_mongodb.insert_one(book_dict)

    client_mongodb.close()
    print("成功建立bookstore数据库并插入数据.")
