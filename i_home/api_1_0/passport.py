# -*- coding:utf-8 -*-
from flask import current_app
from flask import session

from i_home import redis_store, db
from i_home.api_1_0 import api

from flask import request, jsonify

from i_home.models import User
from i_home.utils.response_code import RET


@api.route("/user", methods=["POST"])
def register():
    # 获取参数
    data = request.json
    mobile = data.get("mobile")
    phone_code = data.get("phonecode")
    password = data.get("password")

    # 检验参数
    if not all([mobile, phone_code, password]):
        return jsonify(errno=RET.DATAERR, errmsg="参数不全")

    # 根据手机号在redis中获取手机验证码
    try:
        redis_phone_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取验证码错误")
    if not redis_phone_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码过期")

    if phone_code != redis_phone_code:
        return jsonify(errno=RET.DATAERR, errmsg="验证码错误")

    # 实例化用户对象
    user = User()
    user.name = mobile
    user.mobile = mobile
    user.password = password
    # 保存用户信息
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="保存失败")
    # 保存session信息
    session["name"] = mobile
    session["user_id"] = user.id
    session["mobile"] = mobile

    return jsonify(errno=RET.OK, errmsg="OK")