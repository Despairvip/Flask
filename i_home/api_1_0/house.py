# -*- coding:utf-8 -*-
from flask import current_app, jsonify

from i_home import redis_store
from i_home.api_1_0 import api
from i_home.constants import AREA_INFO_REDIS_EXPIRES
from i_home.models import Area
from i_home.utils.response_code import RET


@api.rou("/areas")
def get_areas():
    # 城区信息缓存到redis中
    try:
        areas_dict = redis_store.get('area_info')
    except Exception as e:
        current_app.logger.error(e)
    if areas_dict:
        return jsonify(errno=RET.OK, errmsg="获取成功", data=eval(areas_dict))

    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")

    areas_dict = []
    for area in areas:
        areas_dict.append(area.to_dict())

    # 数据保存到redis中
    try:
        redis_store.set('area_info', areas_dict, AREA_INFO_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg="获取成功", data=areas_dict)
