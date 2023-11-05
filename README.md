# Bookstore
Comtemporary Database Management System Project —— ECNU DASE

## bookstore结构
```shell
bookstore
  |-- be                            后端
        |-- model                     后端逻辑代码
        |-- view                      访问后端接口
        |-- ....
  |-- doc                           JSON API规范说明
  |-- fe                            前端访问与测试代码
        |-- access
        |-- bench                     效率测试
        |-- data                    
            |-- bookname.db                 sqlite 数据库(bookname.db，较少量的测试数据)
            |-- book_lx.db              sqlite 数据库(book_lx.db， 较大量的测试数据，要从网盘下载)
            |-- scraper.py              从豆瓣爬取的图书信息数据的代码
        |-- test                      功能性测试（包含对前60%功能的测试，不要修改已有的文件，可以提pull request或bug）
        |-- conf.py                   测试参数，修改这个文件以适应自己的需要
        |-- conftest.py               pytest初始化配置，修改这个文件以适应自己的需要
        |-- ....
  |-- ....
```
## 还需要实现的功能（已实现的功能请check！）
- [x] **1)用户权限接口，如注册、登录、登出、注销**

- [x] **2)买家用户接口，如充值、下单、付款**

- [x] **3)卖家用户接口，如创建店铺、填加书籍信息及描述、增加库存**

通过对应的功能测试，所有 test case 都 pass

- [x] **4)实现后续的流程 :发货 -> 收货**

- [x] **5)搜索图书**

用户可以通过关键字搜索，参数化的搜索方式；
如搜索范围包括，题目，标签，目录，内容；全站搜索或是当前店铺搜索。
如果显示结果较大，需要分页
(使用全文索引优化查找)

**这个功能很大概率还要后期根据数据库的结构调整，目前店铺的数据格式为：**
```shell
{
                "store_id": "store1",
                "book_info": "Book Info 1",
                "stock_level": 100,
                'id': "Book1",
                'title': "Book1",
                'author': "",
                'publisher': "",
                'original_title': "",
                'translator': "",
                'pub_year': "",
                'pages': "",
                'price': "",
                'binding': "",
                'isbn': "",
                'author_intro': "",
                'book_intro': "",
                'content': "",
                'tags': "",
                'picture': ""
            },
``` 
**负责3功能的同学在设计store数据库的时候如果有更改务必要提醒一下**


- [x] **6)订单状态，订单查询和取消定单**

用户可以查自已的历史订单，用户也可以取消订单。

取消定单可由买家主动地取消定单，或者买家下单后，经过一段时间超时仍未付款，定单也会自动取消。

## 创作者须知
- assignment.md中是作业的说明
- 每次实现了一个功能，都需要check上方的功能
- 如果有需要下载的包，卸载requirements2.txt中，不全的话请其他创作者补充(^▽^)
- book_lx.db文件过大，每次git push的时候一定要把该文件删除后再上传（或者在IDE中选择不上传该文件）
- 每次开发之前，都要检查仓库的更新情况，然后在本地拉最新仓库。<span style="color: red;">***记得pull request！！！</span>***
```shell
  git clone <your_link> #下载仓库
  git add . #添加新内容到仓库中
  git push #更新仓库
  git pull origin main #下拉仓库
  ```
