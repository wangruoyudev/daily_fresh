from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from apps.goods.models import GoodsSKU
from django_redis import get_redis_connection
# Create your views here.


class CreateOrderView(LoginRequiredMixin, View):
    def post(self, request):
        print('====>CreateOrderView-post:', request.POST)
        # goods_id_list = request.POST.get('sku_id', None)
        goods_id_list = request.POST.getlist('sku_id', [])
        print('===>goods_id_list:', goods_id_list)
        if goods_id_list is not None:
            conn = get_redis_connection('default')
            cart_key = 'cart_id%s' % request.user.id
            goods_sku_list = list()
            for goods_id in goods_id_list:
                try:
                    goods_sku = GoodsSKU.objects.get(id=goods_id)
                    goods_count = conn.hget(cart_key, goods_id)
                    goods_sku.cart_goods_count = goods_count
                    goods_sku_list.append(goods_sku)
                except GoodsSKU.DoesNotExist:
                    continue
        print('====>goods_sku_list:', goods_sku_list)
        context = {'goods_sku_list': goods_sku_list}
        return render(request, 'order/place_order.html', context)

