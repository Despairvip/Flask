# -*- coding:utf-8 -*-
import functools

from flask import g
from flask import session, jsonify
from werkzeug.routing import BaseConverter

from i_home.utils.response_code import RET


class RegexConverter(BaseConverter):
    # 自定义正则转换器
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]


def login_session_check(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
        else:
            g.user_id = user_id
            return f(*args, **kwargs)

    return wrapper
