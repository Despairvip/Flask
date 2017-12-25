# -*- coding:utf-8 -*-
from flask import current_app
from flask import session

from i_home import redis_store, db
from i_home.api_1_0 import api

from flask import request, jsonify

from i_home.models import User
from i_home.utils.response_code import RET


@api.route("/session", methods=['DELETE'])
def logout():
    session.pop('user_id', None)
    session.pop('user', None)
    session.pop('mobile', None)

    return jsonify(errno=RET.OK, errmsg="OK")


@api.route('/session')
def check_login():
    user_id = session.get('user_id')
    name = session.get("name")
    if not all([user_id, name]):
        return jsonify(errno=RET.SESSIONERR, errmsg="未登录")

    return jsonify(errno=RET.OK, errmsg="OK", data={"name": name})


# 用户登录
@api.route('/session', methods=["POST"])
def login():
    # 获取前端参数
    data = request.json
    mobile = data.get("mobile")
    password = data.get("password")
    # 检验参数
    if not all([mobile, password]):
        return jsonify(errno=RET.DATAERR, errmsg="数据错误")

    # 根据电话号码查找数据库
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询错误")
    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户未注册")

    if not user.check_passowrd(password):
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")

    # 保存状态
    session['user_id'] = user.id
    session['name'] = mobile
    session['mobile'] = mobile

    return jsonify(errno=RET.OK, errmsg="登录成功")


# 用户注册
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
