from django.urls import path,re_path
from .views import GoodsDetail

app_name = 'goods'
urlpatterns = [
    path('detail', GoodsDetail.as_view(), 'detail')
]