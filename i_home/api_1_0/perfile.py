# -*- coding:utf-8 -*-
from flask import current_app, jsonify
from flask import g
from flask import request

from i_home import db
from i_home.api_1_0 import api
from i_home.constants import QINIU_DOMIN_PREFIX
from i_home.models import User
from i_home.utils.image_storage import storage_image
from i_home.utils.common import login_session_check
from i_home.utils.response_code import RET


@api.route("/user/avatar", methods=['POST'])
@login_session_check
def save_avatar():
    # 现判断用户是否登录
    # 获取用户传过来的参数
    try:
        avatar = request.files.get('avatar')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="图片上传失败")

    # 根据session信息来判断用户
    user_id = g.user_id
    # 上传图片到七牛云
    try:
        url = storage_image(avatar)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="图片保存失败")

    # 根据用户消息从数据库中获取用户信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="用户查询失败")

    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")
    # 更改用户图像信息
    user.avatar_url = url
    # 数据库提交
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="图片保存失败")
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="OK", data={'avatar_url': QINIU_DOMIN_PREFIX + url})
