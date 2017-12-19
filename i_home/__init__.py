# -*- coding:utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler

import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session

from config import config_dict

# 数据库
db = SQLAlchemy()
# 全局可用的redis
redis_store = None
# csrf保护
csrf = CSRFProtect()

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/logs", maxBytes=1024 * 1024 * 100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)


def create_app(config):
    app = Flask(__name__)

    app.config.from_object(config_dict[config])
    db.init_app(app)
    csrf.init_app(app)

    global redis_store
    redis_store = redis.StrictRedis(host=config_dict[config].REDIS_HOST, port=config_dict[config].REDIS_PORT)
    Session(app)
    return app
