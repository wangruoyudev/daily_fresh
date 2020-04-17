from django.shortcuts import render
from django.views.generic import View
# from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.http import HttpResponse
from apps.goods.models import GoodsSKU, GoodsType, GoodsImage, Goods, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from django.core.cache import cache
from django_redis import get_redis_connection


class IndexView(View):
    def get(self, request):
        if not request.user.is_authenticated: # 登录就返回index，没登录就返回index_static
            print('====>返回静态的首页')
            return render(request, 'index_static.html')

        print('====>获取查询数据库的首页')
        context = cache.get('index_cache')

        if context is None:  # 缓存不存在或者已过期
            print('缓存不存在，重新读取数据库设置缓存')
            goods_type_list = GoodsType.objects.all()
            goods_banner_list = IndexGoodsBanner.objects.all().order_by('index')
            goods_promotion_list = IndexPromotionBanner.objects.all().order_by('-index')

            for goods_type in goods_type_list:
                type_title_list = IndexTypeGoodsBanner.objects.filter(type=goods_type, display_type=0).order_by('index')
                type_image_list = IndexTypeGoodsBanner.objects.filter(type=goods_type, display_type=1).order_by('index')
                goods_type.type_title_list = type_title_list
                goods_type.type_image_list = type_image_list
            context = {'goods_type_list': goods_type_list,
                       'goods_banner_list': goods_banner_list,
                       'goods_promotion_list': goods_promotion_list}
            cache.set('index_cache', context, 3600)  # 缓存一个小时

        cart_count = 0
        if request.user.is_authenticated: #  读取缓存中购物车的记录
            con = get_redis_connection('default')
            cart_key = 'cart_id%s' % request.user.id
            cart_count = con.hlen(cart_key)

        context.update(cart_count=cart_count)

        return render(request, 'user/index.html', context)


class GoodsDetailView(View):
    def get(self, request, goods_id):
        print('===>goods_id:', goods_id)
        return render(request, 'goods/detail.html')
