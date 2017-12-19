# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import Config


app = Flask(__name__)

app.config.from_object(Config)
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
csrf = CSRFProtect
Session(app)
db = SQLAlchemy(app)

manager = Manager(app)
Migrate(app, db)
manager.add_command(db, MigrateCommand)


@app.route("/")
def index():
    return "index"


if __name__ == '__main__':
    # manager.run()
    app.run()