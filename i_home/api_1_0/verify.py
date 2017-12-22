# -*- coding:utf-8 -*-
import random
import re

from flask import abort, jsonify, json
from flask import current_app
from flask import make_response
from i_home import constants
from i_home import redis_store
from i_home.models import User
from i_home.utils.response_code import RET
from i_home.api_1_0 import api
from flask import request
from i_home.utils.captcha.captcha import captcha


@api.route("/imagecode")
def get_image_code():
    # 获取前端传入的验证码编号
    args = request.args
    cur = args.get("cur")
    pre = args.get("pre")
    # 判断传入的参数是否有值
    if not cur:
        abort(403)

    # 生成图片验证码
    _, text, image = captcha.generate_captcha()
    current_app.logger.debug(text)
    # 吧图片验证码和编码存到redis中
    try:
        redis_store.delete("Image_code" + pre)
        redis_store.set("Image_code" + cur, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="存入数据库出错")
    # 返回验证码图片
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response


@api.route("/smscode", methods=["POST"])
def get_sms_code():
    # 获取手机号．图片验证编码，图片验证码内容
    json_data = request.data
    data = json.loads(json_data)
    mobile = data.get("mobile")
    image_id = data.get("image_code_id")
    image_content = data.get("image_code")

    # 检验内容是否正确
    if not all([mobile, image_content, image_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not re.match("^1[3578][0-9]{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号码格式错误")

    try:
        redis_image_content = redis_store.get("Image_code" + image_id)
        if redis_image_content:
            redis_store.delete("Image_code" + image_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取验证码错误")
    if not redis_image_content:
        return jsonify(errno=RET.PARAMERR, errmsg="验证码已过期")

    # 对比redis中的验证码内容
    if image_content.lower() != redis_image_content.lower():
        return jsonify(errno=RET.PARAMERR, errmsg="验证码错误")

    # 查询是否已经注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        user = None
    if user:
        return jsonify(errno=RET.DATAERR, errmsg="手机号码已经注册")

    # 生成短信验证码
    result = random.randint(0, 9999)
    sms_code = "%06d" % result
    current_app.logger.debug("短信验证码的内容是：%s" % sms_code)
    # 保存短信验证码内容
    try:
        redis_store.set("SMS_" + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码失败")
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="OK")
