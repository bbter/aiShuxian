from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .serializer import OrderItemSerializer
from django.urls import reverse
from .util import *
from .models import *


# Create your views here.
def home(request):
    tops = Wheel.objects.all()
    navs = Nav.objects.all()
    mustbuys = MustBuy.objects.all()
    shops = Shop.objects.all()
    infos = MainShow.objects.all()
    data = {
        "title": "首页",
        "tops": tops,
        "navs": navs,
        "mustbuys": mustbuys,
        "shop_0": shops.first(),
        "shop_1_3": shops[1:3],
        "shop_4_7": shops[3:7],
        "shop_7_11": shops[7:],
        "infos": infos
    }
    return render(request, "home/home.html", data)


def market_with_params(request, type_id, sub_type_id, sort):
    types = GoodsTypes.objects.all()
    # 查询具体分类的数据
    goods_type = types.filter(typeid=type_id).first()
    # 获取二级分类的数据
    sub_types = goods_type.childtypenames.split("#")
    sub_type_datas = [i.split(":") for i in sub_types]
    # for i in sub_types:
    #     sub_type_datas.append(i.split(":"))
    print(sub_type_datas)
    # 根据分类的id找商品数据
    goods = Goods.objects.filter(categoryid=type_id)
    # 如果点击的不是全部分类那么才进行二级分类的过滤
    if sub_type_id != '0':
        goods = goods.filter(childcid=sub_type_id)

    # 做排序
    if sort == '1':
        goods = goods.order_by("price")
    elif sort == '2':
        goods = goods.order_by("-productnum")
    else:
        pass

    if request.user.is_authenticated:
        # 查这个人的购物车数据
        if hasattr(request.user, 'cart_set'):
            # 把他购物车数据都拿出来
            cart_data = request.user.cart_set.all()
            # 遍历我们的商品数据
            for good in goods:
                # 去购物车的数据里查查这个商品是不是在购物车里
                cart_goods = cart_data.filter(goods=good)
                if cart_goods.exists():
                    # 将数据赋值给我们新的属性
                    good.cart_num = cart_goods.first().num

    data = {
        "title": "闪购",
        "types": types,
        "select_type_id": type_id,
        "goods": goods,
        "sub_types": sub_type_datas,
        "select_sub_type_id": sub_type_id,
        'current_sort': sort,
    }
    return render(request, "market/market.html", data)


def market(request):
    # types = GoodsTypes.objects.all()
    #     # data = {
    #     #     "title": "闪购",
    #     #     "types":types
    #     # }
    #     # return render(request, "market/market.html", data)
    return redirect(reverse("axf:market_with_params", kwargs={"type_id": 104749, "sub_type_id": 0, "sort": 0}))


@login_required(login_url='/axf/login')
def cart(request):
    user = request.user
    cartitems = Cart.objects.filter(user_id=str(user.id))
    is_select_all = True
    # 判断全选按钮的状态
    if cartitems.filter(is_select=False).exists():
        is_select_all = False
    money = get_all_sum_money(cartitems)
    data = {
        "title": "购物车",
        "cartitems": cartitems,
        "is_select_all": is_select_all,
        "money": "%.2f" % money
    }
    return render(request, "cart/cart.html", data)


def mine(request):
    # 知道用户是不是登录了
    # 用户的信息 名字和头像
    user = request.user
    # is_login = False
    # uname = ''
    # icon = ''
    # if user.is_authenticated():
    #     is_login = True
    #     uname = user.username
    #     icon = user.icon
    is_login, name, icon = (True, user.username, user.icon.url) if user.is_authenticated() else (False, "", "")
    # print(icon)
    # print(type(icon))
    funs = Fun.objects.filter(is_use=True)
    data = {
        "title": "我的",
        "is_login": is_login,
        "name": name,
        "icon": "http://{url}/static/uploads/{icon}".format(url=request.get_host(), icon=icon),
        "funs": funs
    }
    return render(request, "mine/mine.html", data)


def logout_api(request):
    logout(request)
    return redirect(reverse("axf:mine"))


def register_view(request):
    return render(request, 'user/register.html')


def login_view(request):
    return render(request, 'user/login.html')


# 订单
@login_required(login_url='/axf/login')
def order_view(request):
    user = request.user
    address = Address.objects.get(user_id=user.id, is_default=True)
    order = Order.objects.create(
        user_id=user.id,
        number=get_order_number(),
        address=address,
    )
    cart_items = Cart.objects.select_related("goods").filter(user_id=user.id, is_select=True)
    # 判断选择商品是否存在
    if not cart_items.exists():
        raise Exceptions("您未选中任何商品")
    order_items = []
    for i in cart_items:
        # 判断库存
        desc = None
        if i.num > i.goods.storenums:
            desc = "当前库存不足请稍后购买"
        order_item = OrderItem.objects.create(
            order_id=order.id,
            goods_num=i.num,
            goods_id=i.goods_id,
            price=i.goods.price,
            desc=desc
        )
        order_items.append(order_item)
    sum_money = get_all_sum_money(cart_items)
    # 清空购物车选中的数据
    cart_items.delete()
    data = {
        'sum_money': sum_money,
        'order_items': OrderItemSerializer(order_items, many=True).data,
        "order_number": order.number
    }
    print(data)
    return render(request, "order/order.html", data)
