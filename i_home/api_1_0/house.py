# -*- coding:utf-8 -*-
from flask import current_app, jsonify
from flask import g
from flask import request

from i_home import redis_store, db
from i_home.api_1_0 import api
from i_home.constants import AREA_INFO_REDIS_EXPIRES
from i_home.models import Area, House, Facility
from i_home.utils.common import login_session_check
from i_home.utils.response_code import RET


@api.route("/areas")
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


@api.route('/houses', methods=['POST'])
@login_session_check
def get_houses_info():
    user_id = g.user_id
    data = request.json
    title = data.get('title')
    price = data.get('price')
    area_id = data.get('area_id')
    address = data.get('address')
    room_count = data.get('title')
    acreage = data.get('acreage')
    unit = data.get('unit')
    capacity = data.get('capacity')
    beds = data.get('beds')
    deposit = data.get('deposit')
    min_days = data.get('min_days')
    max_days = data.get('max_days')
    facility = data.get('facility')

    if not all([title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit,
                min_days, max_days, facility]):
        return jsonify(errno=RET.DATAERR, errmsg="参数不正确")

    # 转换price的单位
    try:
        price = int(float(price)*100)
        deposit = int(float(deposit)*100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="参数有误")

    house = House()
    house.user_id = user_id
    house.title = title
    house.price = price
    house.area_id = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    if facility:
        house.facilities = Facility.query.filter(Facility.id.in_(facility)).all()

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="存储失败")
    return jsonify(errno=RET.OK, errmsg="发布成功", data={'house_id': house.id})


