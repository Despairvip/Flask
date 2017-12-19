# -*- coding:utf-8 -*-
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from i_home import app, db

manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route("/")
def index():
    return "index"


if __name__ == '__main__':
    manager.run()
    # app.run()

# -*- coding:utf-8 -*-
#
# import redis
# from flask import Flask, session
# from flask_sqlalchemy import SQLAlchemy
# from flask_wtf.csrf import CSRFProtect
# from flask_session import Session
# from flask_script import Manager
# from flask_migrate import Migrate, MigrateCommand
# from config import Config
#
#
# app = Flask(__name__)
# app.config.from_object(Config)
#
# # 初始化数据库连接
# db = SQLAlchemy(app)
# # 初始化redis
# redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# # 开启CSRF保护
# csrf = CSRFProtect(app)
# # 给当前app的session设置保存路径
# Session(app)
#
# manager = Manager(app)
# # 集成数据库的迁移
# Migrate(app, db)
# manager.add_command('db', MigrateCommand)
#
#
# @app.route("/index", methods=["GET", "POST"])
# def index():
#     session["name"] = "xiaohua"
#     redis_store.set('name', 'xiaofang')
#     return "index"
#
#
# if __name__ == '__main__':
#     manager.run()
