from rest_framework import serializers
from .models import *


class CartSerializer(serializers.ModelSerializer):
    # 当默认情况不满足的时候我们可以自己重写对应的字段
    is_select = serializers.BooleanField(default=True,required=False)
    class Meta:
        model = Cart
        fields = ("id","goods","num","user","is_select")

class GoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = ('productimg','productlongname','price')


class OrderItemSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer()
    class Meta:
        model = OrderItem
        fields = ('id','goods_num','goods','desc')