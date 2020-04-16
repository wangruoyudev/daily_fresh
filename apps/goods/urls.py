from django.urls import path, re_path
from .views import GoodsDetailView

app_name = 'goods'
urlpatterns = [
    path('detail', GoodsDetailView.as_view(), name='detail')
]