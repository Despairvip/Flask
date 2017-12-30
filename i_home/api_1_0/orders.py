# -*- coding:utf-8 -*-
import datetime
from flask import current_app, jsonify
from flask import g
from flask import request

from i_home import db
from i_home.api_1_0 import api
from i_home.models import House, Order
from i_home.utils.common import login_session_check
from i_home.utils.response_code import RET


@api.route("/orders", methods=["POST"])
@login_session_check
def get_new_orders():
    user_id = g.user_id
    data = request.json
    house_id = data.get("house_id")
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")

    if not all([house_id, start_date_str, end_date_str]):
        return jsonify(errno=RET.DATAERR, errmsg="参数不全")
    try:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        assert end_date > start_date, Exception("结束时间大于开始时间")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据错误")

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询错误")
    if not house:
        return jsonify(errno=RET.DATAERR, errmsg="房屋不存在")

    # 判断房屋的冲突订
    try:
        filters = [Order.house_id == house_id, Order.begin_date < end_date, Order.end_date > start_date]
        order_count = Order.query.filter(*filters).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据错误")

    if order_count > 0:
        return jsonify(errno=RET.DATAERR, errmsg="房屋已被预订")

    order = Order()
    order.user_id = user_id
    order.house_id = house_id
    order.begin_date = start_date
    order.end_date = end_date
    order.days = (end_date - start_date).days
    order.house_price = house.price
    order.amount = order.days * house.price

    house.order_count += 1

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存失败")
    return jsonify(errno=RET.OK, errmsg="OK")
