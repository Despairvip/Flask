# -*- coding:utf-8 -*-
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


def create_app(config):

    app = Flask(__name__)

    app.config.from_object(config_dict[config])
    db.init_app(app)
    csrf.init_app(app)

    global redis_store
    redis_store = redis.StrictRedis(host=config_dict[config].REDIS_HOST, port=config_dict[config].REDIS_PORT)
    Session(app)
    return app