# -*- coding:utf-8 -*-
from flask import current_app, jsonify
from flask import g
from flask import request
from flask import session

from i_home import redis_store, db
from i_home.api_1_0 import api
from i_home.constants import AREA_INFO_REDIS_EXPIRES, QINIU_DOMIN_PREFIX, HOUSE_DETAIL_REDIS_EXPIRE_SECOND
from i_home.models import Area, House, Facility, HouseImage
from i_home.utils.image_storage import storage_image
from i_home.utils.common import login_session_check
from i_home.utils.response_code import RET


@api.route("/houses/<int:house_id>")
def detail_house_info(house_id):
    user_id = session.get("user_id", -1)

    try:
        house_dict = redis_store.get(("house_detail_%d" % house_id))
        if house_dict:
            return jsonify(errno=RET.OK, errmsg="ok", data={"user_id": user_id, "house": house_dict})
    except Exception as e:
        current_app.logger.error(e)

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")
    if not house:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    house_dict = house.to_full_dict()

    try:
        redis_store.set(("house_detail_%d") % house_id, house_dict, HOUSE_DETAIL_REDIS_EXPIRE_SECOND)
    except Exception as e:
        current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg="0", data={"house": house_dict, "user_id": user_id})


@api.route("/houses/<int:house_id>/images", methods=['POST'])
@login_session_check
def release_house_images(house_id):
    try:
        images_file = request.files.get("house_image").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="获取参数失败")

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取房屋信息失败")

    if not house:
        return jsonify(errno=RET.DATAERR, errmsg="房屋不存在")

    try:
        url = storage_image(images_file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传失败")

    if not house.index_image_url:
        house.index_image_url = url

    house_image = HouseImage()
    house_image.house_id = house_id
    house_image.url = url

    try:
        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="存储失败")
    return jsonify(errno=RET.OK, errmsg="保存成功", data={'url': QINIU_DOMIN_PREFIX + url})


@api.route("/areas")
def release_areas():
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

    json_dict = request.json
    title = json_dict.get('title')
    price = json_dict.get('price')
    address = json_dict.get('address')
    area_id = json_dict.get('area_id')
    room_count = json_dict.get('room_count')
    acreage = json_dict.get('acreage')
    unit = json_dict.get('unit')
    capacity = json_dict.get('capacity')
    beds = json_dict.get('beds')
    deposit = json_dict.get('deposit')
    min_days = json_dict.get('min_days')
    max_days = json_dict.get('max_days')

    if not all([title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit,
                min_days, max_days]):
        return jsonify(errno=RET.DATAERR, errmsg="参数不正确")

    # 转换price的单位
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="参数有误")

    house = House()
    house.user_id = user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    facility = json_dict.get('facility')
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
