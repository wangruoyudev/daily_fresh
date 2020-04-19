from django.urls import path, re_path
from .views import GoodsDetailView, IndexView, GoodsTypeListView, AddCartView

app_name = 'goods'
urlpatterns = [
    path('index/', IndexView.as_view(), name='index'),
    re_path(r'^detail/(?P<goods_id>\d+)$', GoodsDetailView.as_view(), name='detail'),
    re_path(r'^type_list/(?P<type_id>\d+)/(?P<page_num>\d+)$', GoodsTypeListView.as_view(), name='list'),
    path('add_cart/', AddCartView.as_view(), name='add_cart'),
]