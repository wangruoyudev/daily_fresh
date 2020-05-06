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


def failed_msg(code, msg):
    return {
        'ret': 'failed',
        'code': code,
        'msg': msg,
    }


class UpdateCartView(View):
    def post(self, request):
        context = {
            'ret': 'failed'
        }

        if not request.user.is_authenticated:
            return JsonResponse(failed_msg('1', '用户未登录'))

        goods_id = request.POST.get('cart_goods_id', None)
        goods_count = request.POST.get('cart_goods_count', None)
        print('===>goods_id:', goods_id)
        print('==>DelCartView-post:', request.POST)
        try:
            goods_count = int(goods_count)
        except ValueError:
            goods_count = None
        if goods_id is not None and goods_count is not None:
            cart_key = 'cart_id%s' % request.user.id
            conn = get_redis_connection('default')
            conn.hset(cart_key, goods_id, goods_count)
            context.update(ret='success')

        return JsonResponse(context)


class DelCartView(View):
    def post(self, request):
        context = {
            'ret': 'failed'
        }
        if request.user.is_authenticated:
            goods_id = request.POST.get('cart_goods_id', None)
            print('===>goods_id:', goods_id)
            print('==>DelCartView-post:', request.POST)
            if goods_id is not None:
                cart_key = 'cart_id%s' % request.user.id
                conn = get_redis_connection('default')
                conn.hdel(cart_key, goods_id)
                context.update(ret='success')

        return JsonResponse(context)
