# Bookstore
Comtemporary Database Management System Project —— ECNU DASE

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
            |-- book.db                 sqlite 数据库(book.db，较少量的测试数据)
            |-- book_lx.db              sqlite 数据库(book_lx.db， 较大量的测试数据，要从网盘下载)
            |-- scraper.py              从豆瓣爬取的图书信息数据的代码
        |-- test                      功能性测试（包含对前60%功能的测试，不要修改已有的文件，可以提pull request或bug）
        |-- conf.py                   测试参数，修改这个文件以适应自己的需要
        |-- conftest.py               pytest初始化配置，修改这个文件以适应自己的需要
        |-- ....
  |-- ....
```
