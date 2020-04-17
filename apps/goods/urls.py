from django.urls import path, re_path
from .views import GoodsDetailView, IndexView

app_name = 'goods'
urlpatterns = [
    re_path(r'^detail/(?P<goods_id>\d+)/?$', GoodsDetailView.as_view(), name='detail'),
    path('index', IndexView.as_view(), name='index'),
]