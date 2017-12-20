# -*- coding:utf-8 -*-

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from i_home import create_app, db
from i_home import models

app = create_app("development")
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route("/")
def index():
    return "index"


if __name__ == '__main__':
    manager.run()
