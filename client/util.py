import uuid
import hashlib
import datetime

def get_unique_str():
    uuid_val = str(uuid.uuid4()).encode()

    md5 = hashlib.md5()

    md5.update(uuid_val)
    return md5.hexdigest().lower()

def get_all_sum_money(cartitems):
    sum_money = 0
    # 计算选择商品的总价
    for i in cartitems.filter(is_select=True):
        sum_money += (i.num * i.goods.price)
    return sum_money


def get_order_number():
    uuid_str = uuid.uuid4().hex
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M")
    # 时间加上随机字符
    number = now_str + uuid_str[:20]
    return number