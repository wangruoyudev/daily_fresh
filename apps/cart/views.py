from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django_redis import get_redis_connection
from apps.goods.models import GoodsSKU
# Create your views here.


class CartInfoView(LoginRequiredMixin, View):
    def get(self, request):
        con = get_redis_connection('default')
        cart_key = 'cart_id%s' % request.user.id
        cart_list = con.hgetall(cart_key)
        print('====>cart_list:', cart_list)
        goods_sku_list = list()
        total_count = 0
        for key in cart_list:  # 遍历购物车
            print('key: ', key.decode(), '   -value: ', cart_list[key].decode())
            try:
                goods_sku = GoodsSKU.objects.get(id=key.decode())  # 去除购物车的sku对象
            except GoodsSKU.DoesNotExist:
                continue
            goods_sku.cart_count = cart_list[key].decode()
            goods_sku_list.append(goods_sku)
            total_count += int(cart_list[key].decode())

        context = {
            'goods_sku_list': goods_sku_list,
            'total_count': total_count,
        }
        return render(request, 'cart/cart.html', context)


class DelCartView(View):
    def post(self, request):
        if request.user.is_authenticated:
            goods_id = request.POST.get('cart_goods_id', None)
            print('===>goods_id:', goods_id)
            context = {
                'ret': 'failed'
            }
            if goods_id is not None:
                cart_key = 'cart_id%s' % request.user.id
                conn = get_redis_connection('default')
                conn.hdel(cart_key, goods_id)
                context.update(ret='success')
        else:
            context = {
                'ret': 'failed'
            }

        return JsonResponse(context)
