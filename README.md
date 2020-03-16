# 简介
Web UI 表情包管理器。

功能：
- 浏览图片。
- 添加、删除图片。
- 给图片打标签，并可以按标签搜索。
- 图片分组。

# 安装：
要求：Python 3.6 及以上。

本软件使用 PyPI 进行分发，所以你可以使用 pip 来安装。但是更建议使用 [pipx](https://github.com/pipxproject/pipx) 将其安装到一个单独的虚拟环境中，避免污染全局系统依赖，如下：
```
$ pipx install meme-manager
```

验证安装成功：
```bash
$ meme-manager --version
# 或
$ meme-manager --help
```

# 使用：
```bash
# 初始化 sqlite 数据库：
$ meme-manager initdb foo.sqlite

# 运行：
$ meme-manager run foo.sqlite

# URL：http://localhost:5000/index.html
```

# 开发：
说明：
后端使用 Python Flask + waitress，前端使用 React + Antd 开发。

后端：
```bash
$ git clone https://github.com/valleygtc/meme-manager.git
$ cd meme-manager

# create venv
$ python3 -m venv .venv
$ source .venv/bin/activate
# install meme-manager and its dependencies.
$ pip install --editable .

# run unittest
$ python -m unittest discover

# ENV
$ cp env.sh.example env.sh
$ vi env.sh # 填写好程序运行所需环境变量。
$ source env.sh # 读入环境变量。

# init db memes.sqlite
$ meme-manager initdb

# run on db memes.sqlite
$ flask run
```

前端：

见：https://github.com/valleygtc/meme-manager-frontend

# 构建与发布：
prerequsite：
```
$ pip install --user --upgrade setuptools wheel

$ pipx install twine
```

build and upload to pypi:
```bash
# 首先要 build 前端。
# 然后把前端 build 出来的 build/ 目录复制到 src/meme-manager 目录下，并改名为 frontend。

# build
$ python3 setup.py sdist bdist_wheel

# upload to pypi
$ twine upload dist/*
```
