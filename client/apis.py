from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse, QueryDict
from django.urls import reverse
from django.views import View
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from .util import get_all_sum_money
from .authentications import LoginAuthentication
from .serializer import *

from .util import *
from .models import *
from .tasks import *
from django.core.cache import cache

class LoginAPI(View):
    def post(self, request):
        # 解析参数
        u_name = request.POST.get("uname")
        pwd = request.POST.get("password")
        # 校验数据
        if u_name and len(u_name) >= 3:
            # 校验用户
            user = authenticate(username=u_name, password=pwd)
            # 进行登录
            if user:
                login(request, user)
                data = {
                    "code": 0,
                    "msg": 'ok',
                    "data": reverse("axf:mine")
                }
                return JsonResponse(data)
            else:
                data = {
                    "code": 1,
                    "msg": '用户名或密码错误',
                }
                return JsonResponse(data)
        else:
            data = {
                "code": 1,
                "msg": '用户名过短',
            }
            return JsonResponse(data)


class CheckNameAPI(View):
    def post(self,request):
        uname = request.POST.get("uname")
        if MyUser.objects.filter(username=uname).exists():
            data = {
                'code': 1,
                'msg': '此账号已经被注册'
            }
            return JsonResponse(data)
        data = {
            'code': 0,
            'msg': ''
        }
        return JsonResponse(data)

class RegisterAPI(View):
    def post(self,request):
        # 解析参数
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        confirm_pwd = request.POST.get("confirm_pwd")
        email = request.POST.get("email")
        icon = request.FILES.get("icon")
        print(icon)
        # 校验数据合法性
        if username and len(username)>=3 and pwd and pwd == confirm_pwd:
            # 校验用户名是否可用
            if MyUser.objects.filter(username=username).exists():
                data = {
                    'code':1,
                    'msg':'此账号已经被注册'
                }
                return JsonResponse(data)
            # 创建用户
            user = MyUser.objects.create_user(
                username=username,
                password=pwd,
                email=email,
                icon = icon,
                is_active=False
            )
            # 发送激活邮件
            schema = "https//" if request.is_secure() else "http://"
            unique = get_unique_str()
            url_path = reverse("axf:active", args=(unique,))
            url = "{schema}{host_and_port}{url_path}".format(
                host_and_port=request.get_host(),
                url_path=url_path,
                schema=schema
            )
            print(url)
            send_verify_email.delay(email,url)
            cache.set(unique, user.id, settings.VERIFY_ALIVE)

            # 跳转到登录页面
            data = {
                "code":0,
                "data":reverse("axf:login")
            }
            return JsonResponse(data)
        else:
            data = {
                "code": 1,
                "data": "数据不合法"
            }
            return JsonResponse(data)


# 激活的API
def active_api(request,active):
    u_id = cache.get(active)
    if u_id:
        MyUser.objects.filter(id=int(u_id)).update(
            is_active = True
        )
        return HttpResponse("激活成功")
    else:
        return HttpResponse("链接失效,请重新注册")


class ItemCart(CreateAPIView,UpdateAPIView):
    queryset = Cart.objects.all()
    authentication_classes = [LoginAuthentication]
    serializer_class = CartSerializer
    def post(self, request, *args, **kwargs):
        # 允许修改我们的请求参数
        request.data._mutable =True
        user = request.user
        # 判断用户是否登录
        if not user:
            res = {
                "msg":"not login",
                "code":1,
                "data":reverse("axf:login")
            }
            return Response(res)
        # 为了满足我们序列化器的字段需求
        request.data['user'] = user.id
        # 获取商品
        goods_id = request.data.get("goods")
        goods = Goods.objects.filter(pk=goods_id).first()
        num = int(request.data.get("num"))
        if num > goods.storenums:
            res = {
                "code":2,
                "msg":"商品库存不足",
                "date":None
            }
            return Response(res)
        cart_items = Cart.objects.filter(
            user = user,
            goods_id = goods_id,

        )
        # 如果不是第一次添加,那就修改对应的数据的商品数量
        if cart_items.exists():
            cart_item = cart_items.first()
            cart_item.num += int(num)
            cart_item.save()
            res = {
                "code":0,
                "msg":"ok",
                "data":self.get_serializer(cart_item).data
            }
            return Response(res)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            res = {
                'code':0,
                'msg':'ok',
                'data':serializer.data
            }
            return Response(res,status=status.HTTP_201_CREATED,headers=headers)

    def put(self, request, *args, **kwargs):
        request.data._mutable = True
        user = request.user
        # 判断用户是否登录
        if not user:
            res = {
                "msg": "not login",
                "code": 1,
                "data": reverse("axf:login")
            }
            return Response(res)
        num = int(request.data.get('num'))
        if num < 1:
            res = {
                'code':1,
                'msg':"数量不合法",
                'data':''
            }
            return Response(res)
        cart_data = Cart.objects.filter(user_id=user.id,goods_id=request.data.get("goods")).first()
        cart_num = 0
        #修改商品数量
        cart_data.num -= num
        # 判断数量是不是为0
        if cart_data.num == 0:
            cart_data.delete()
        else:
            cart_data.save()
            cart_num = cart_data.num
        res = {
            'code':0,
            'msg':'ok',
            'data':cart_num

        }
        return Response(res)



class CartItemStatusAPI(View):
    def put(self,request):
        params = QueryDict(request.body)
        user = request.user
        cart_id = params.get('cid')
        cart_item = Cart.objects.filter(pk=cart_id).first()
        cart_item.is_select = not cart_item.is_select
        cart_item.save()

        is_select_all = True
        cart_items = Cart.objects.filter(user=user)
        if cart_items.filter(is_select=False):
            is_select_all = False

        money = get_all_sum_money(cart_items)
        res = {
            'code':0,
            'msg':"ok",
            'data':{
                'current_item_status':cart_item.is_select,
                'is_select_all':is_select_all,
                'money':'%.2f' % money
            }
        }
        return JsonResponse(res)



def cart_data_status_api(request):
    # 获取用户
    user = request.user
    if not user.is_authenticated:
        raise Exceptions("您未登录")
    # 判断操作的动作
    carts = Cart.objects.filter(user_id=user.id)
    # 保证购物有有数据
    if not carts.exists():
        raise Exceptions("您的购物车暂无商品,请去购物")

    is_select_all = Cart.objects.filter(is_select=False).exists()
    # 存在没被选中的数据,将商品全选
    carts.update(is_select=is_select_all)
    # 算钱
    sum_money = get_all_sum_money(carts) if is_select_all else 0
    res = {
        'code':0,
        'msg':'ok',
        'data':{
            'is_select_all':is_select_all,
            'sum_money':'%.2f' % sum_money,
        }
    }
    return JsonResponse(res)


class CartDataOptionAPI(View):
    def put(self,request):
        params = QueryDict(request.body)
        user = request.user
        print(user)
        print(params)
        if not user.is_authenticated:
            raise Exceptions("请先登录")
        # 拿到这个id对应购物车的数据
        cart_data = Cart.objects.get(pk=params.get('cid'))
        # 判断操作是加还是减
        print(cart_data)
        option = params.get('option')
        if option == "add":
            cart_data.num += 1
            cart_data.save()
        else:
            cart_data.num -= 1
            if cart_data.num == 0:
                cart_data.delete()
            else:
                cart_data.save()

        # 算总价
        cart_items = Cart.objects.filter(user=user)
        sum_money = get_all_sum_money(cart_items)

        is_select_all = (not cart_items.filter(is_select=False).exists()) and cart_items.exists()
        res = {
            'code': 0,
            'msg': 'ok',
            'data':{
                "sum_money":'%.2f' % sum_money,
                "current_num":cart_data.num,
                'is_select_all':is_select_all
            }
        }
        return JsonResponse(res)










