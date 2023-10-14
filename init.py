import pymongo

def init_mongodb():
    # 连接到MongoDB数据库
    client = pymongo.MongoClient('localhost', 27017)  # 请根据实际情况修改MongoDB的连接URL
    db = client["bookstore"]  # 替换为您的数据库名称

    # 创建用户集合并添加索引
    users = db["users"]
    users.create_index("user_id", unique=True)

if __name__ == "__main__":
    init_mongodb()
    print("成功建立bookstore数据库.")
