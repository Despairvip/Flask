# -*- coding:utf-8 -*-
import datetime
from flask import current_app, jsonify
from flask import g
from flask import request

from i_home import db, redis_store
from i_home.api_1_0 import api
from i_home.models import House, Order
from i_home.utils.common import login_session_check
from i_home.utils.response_code import RET


@api.route("/user/orders")
@login_session_check
def get_orders_list():
    user_id = g.user_id
    role = request.args.get("role")
    if not role:
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")
    if role not in ("custom", "landlord"):
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")
    # 判断时房东还是房客
    try:
        if role == "custom":
            orders = Order.query.filter(Order.user_id == user_id).order_by(Order.create_time.desc()).all()
        elif role == "landlord":
            # 查询当前用户所有房源
            houses = House.query.filter(House.user_id == user_id).all()
            house_ids = [house.id for house in houses]
            # 查询所有房间的订单
            orders = Order.query.filter(Order.house_id.in_(house_ids)).order_by(Order.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="参数错误")
    order_dict = []
    for order in orders:
        order_dict.append(order.to_dict())

    return jsonify(errno=RET.OK, errmsg="Ok", data={'orders': order_dict})


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


@api.route('/orders/comment', methods=["PUT"])
@login_session_check
def order_comment():
    """
    订单评价
    1. 获取参数
    2. 校验参数
    3. 修改模型
    :return:
    """

    # 1. 获取参数
    data_json = request.json
    order_id = data_json.get("order_id")
    comment = data_json.get("comment")

    # 2. 2. 校验参数
    if not all([order_id, comment]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        order = Order.query.filter(Order.id == order_id, Order.status == "WAIT_COMMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据错误")

    if not order:
        return jsonify(errno=RET.NODATA, errmsg="该订单不存在")

    # 3. 修改模型并且保存到数据库
    order.comment = comment
    order.status = "COMPLETE"

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 删除房屋详情信息缓存
    try:
        redis_store.delete("house_detail_%d" % order.house_id)
    except Exception as e:
        current_app.logger.error(e)

    # 4. 返回结果
    return jsonify(errno=RET.OK, errmsg="ok")


@api.route('/orders', methods=["PUT"])
@login_session_check
def change_order_status():
    """
    1. 接受参数：order_id
    2. 通过order_id找到指定的订单，(条件：status="待接单")
    3. 修改订单状态
    4. 保存到数据库
    5. 返回
    :return:
    """
    user_id = g.user_id
    data_json = request.json
    # 取到订单号
    order_id = data_json.get("order_id")
    action = data_json.get("action")

    if not all([order_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # accept / reject
    if action not in ("accept", "reject"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 2. 查询订单
    try:
        order = Order.query.filter(Order.id == order_id, Order.status == "WAIT_ACCEPT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not order:
        return jsonify(errno=RET.NODATA, errmsg="未查询到订单")

    # 查询当前订单的房东是否是当前登录用户，如果不是，不允许操作
    if user_id != order.house.user_id:
        return jsonify(errno=RET.ROLEERR, errmsg="不允许操作")

    # 3 更改订单的状态
    if "accept" == action:
        # 接单
        order.status = "WAIT_COMMENT"
    elif "reject" == action:
        order.status = "REJECTED"
        # 取出原因
        reason = data_json.get("reason")
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="请填写拒单原因")
        # 保存拒单原因
        order.comment = reason

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    return jsonify(errno=RET.OK, errmsg="OK")


