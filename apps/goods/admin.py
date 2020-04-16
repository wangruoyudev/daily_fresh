from django.contrib import admin

from .models import GoodsImage, GoodsType, Goods, GoodsSKU, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
# Register your models here.
from apps.user.tasks import create_static_index_html


# 当这个数据表有改动的时候，就重新生成静态页面
class IndexTypeGoodsAdmin(admin.ModelAdmin):
    '''有保存或者删除首页的数据，就重新生成静态页面'''
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        create_static_index_html.delay(None)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        create_static_index_html.delay(None)


admin.site.register(GoodsType)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(GoodsImage)
admin.site.register(IndexGoodsBanner)
admin.site.register(IndexPromotionBanner)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsAdmin)
