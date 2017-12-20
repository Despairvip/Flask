# -*- coding:utf-8 -*-
# 提供静态页面
from flask import Blueprint
from flask import current_app
from flask import make_response
from flask_wtf.csrf import generate_csrf

# 创建蓝图
html = Blueprint("html", __name__)


@html.route('/<re(".*"):file_name>')
def get_index_html(file_name):
    if not file_name:
        # 如果用户没有输入
        file_name = 'index.html'
    if file_name != "favicon.ico":
        file_name = 'html/' + file_name
    response = make_response(current_app.send_static_file(file_name))
    csrf_token = generate_csrf()

    # csrf_token = generate_csrf()
    # 设置token
    response.set_cookie('csrf_token', csrf_token)
    return response
