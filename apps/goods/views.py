from django.shortcuts import render, redirect, reverse
from django.views.generic import View
# from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.http import HttpResponse
from apps.goods.models import GoodsSKU, GoodsType, GoodsImage, Goods, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from django.core.cache import cache
from django_redis import get_redis_connection


class RedirectIndexView(View):
    def get(self, request):
        return redirect(reverse('goods:index'))


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

        return render(request, 'goods/index.html', context)


class GoodsDetailView(View):
    def get(self, request, goods_id):
        print('===>goods_id:', goods_id)
        try:
            goods_sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoseNotExist:
            return redirect(reverse('goods:index'))
        new_goods_list = GoodsSKU.objects.all().exclude(id=goods_id).order_by('-create_time')[:2]
        type_goods_list = GoodsType.objects.all().order_by('id')
        goods_spu = goods_sku.goods
        context = {
            'goods_sku': goods_sku,
            'new_goods_list': new_goods_list,
            'type_goods_list': type_goods_list,
        }
        cart_count = 0
        if request.user.is_authenticated:  # 读取缓存中购物车的记录
            con = get_redis_connection('default')
            cart_key = 'cart_id%s' % request.user.id
            cart_count = con.hlen(cart_key)

            # 添加最近浏览，用sku的id做value
            browse_key = 'user_browse_%s' % request.user.id
            con.lrem(browse_key, 0, goods_id) # 先删除之前列表里面的goods id
            con.lpush(browse_key,  goods_id) # 再从左侧添加添加goods id
            if con.llen(browse_key) > 5:
                con.rpop(browse_key)

        context.update(cart_count=cart_count)

        return render(request, 'goods/detail.html', context)
