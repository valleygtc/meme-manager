# 简介
Web UI 表情包管理器。

功能：
- 浏览图片。
- 添加、删除图片。
- 给图片打标签，并可以按标签搜索。

# 安装：
```
$ pipx install meme-manager
```

验证安装成功：
```
$ meme-manager --help
```

# 使用：
```bash
# 初始化 sqlite 数据库：
$ meme-manager init_db foo.sqlite

# 运行：
$ meme-manager run foo.sqlite

# 打开浏览器，在地址栏输入：http://localhost:5000/index.html
```

# 开发：
说明：
后端使用 Python Flask + waitress 开发。
前端使用 React + Antd 开发。

后端：
```bash
$ git clone https://github.com/valleygtc/meme-manager.git
$ cd meme-manager

# create venv
$ python3 -m venv .venv
$ source .venv/bin/activate
# install meme-manager and its dependencies.
$ python setup.py

# ENV
$ cp env.sh.example env.sh
$ vi env.sh # 填写好程序运行所需环境变量。
$ source env.sh # 读入环境变量。


$ flask run
$ python -m unittest discover
```

前端：

见：https://github.com/valleygtc/meme-manager-frontend

# 构建与发布：
```bash
# build
$ python3 setup.py sdist bdist_wheel

# upload to pypi
$ python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```
