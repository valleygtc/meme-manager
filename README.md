# 简介
表情包管理器后端


# 部署
```bash
$ git clone <repo>
$ cd meme-manager-backend

$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple # 清华pypi镜像。

$ cp env.sh.example env.sh
$ vi env.sh # 填写好程序运行所需环境变量。

$ source env.sh # 读入环境变量。
$ flask create_table # 创建数据库表。

$ python run.py
```


# 依赖说明
- Flask 框架
- DB：
  - ORM: Flask-SQLAlchemy
  - MySQL + mysql-connector-python
- 部署： waitress


# API
```
Endpoint              Methods  Rule
--------------------  -------  -----------------------
bp_main.add_image     POST     /images/add
bp_main.add_tags      POST     /tags/add
bp_main.delete_image  GET      /images/delete
bp_main.delete_tag    POST     /tags/delete
bp_main.show_images   GET      /images/
bp_main.show_tags     GET      /tags/
static                GET      /static/<path:filename>
```

- [前后端接口格式规定](./interface.md)
- 各个接口具体格式见view.py中的每个**视图函数上方的注释**。


# 开发说明：
- flask debug server: `$ flask run [--host=0.0.0.0]`
- unittest: `python -m unittest discover`
