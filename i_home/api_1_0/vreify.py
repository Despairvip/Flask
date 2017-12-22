# -*- coding:utf-8 -*-
from flask import abort, jsonify
from flask import current_app
from flask import make_response
from i_home import constants
from i_home import redis_store
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
