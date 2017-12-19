# -*- coding:utf-8 -*-
import redis


class Config():
    '''工程信息'''
    DEBUG = True
    SECRET_KEY = "EjpNVSNQTyGi1VvWECj9TvC/+kq3oujee2kTfQUs8yCM6xX9Yjq52v54g+HVoknA"

    '''配置redis数据库'''
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    '''配置数据库信息'''
    # 数据库的配置信息
    # SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/flask"
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    '''配置session'''
    SESSION_TYPE = redis  # 指定session存储位置
    SESSION_USER_SINGER = True  # 让session中的session_id 加密传输
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 86400  # 设置session的过期时间


class DevelopmentConfig(Config):
    """开发模式下的配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产模式下的配置"""
    pass


config_dict = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
