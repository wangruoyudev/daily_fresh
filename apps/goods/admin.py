from django.contrib import admin

from .models import GoodsImage, GoodsType, Goods, GoodsSKU, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
# Register your models here.


admin.site.register(GoodsType)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(GoodsImage)
admin.site.register(IndexGoodsBanner)
admin.site.register(IndexPromotionBanner)
admin.site.register(IndexTypeGoodsBanner)
