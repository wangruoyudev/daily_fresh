from django.urls import path
from .views import CartInfoView, DelCartView

app_name = 'cart'
urlpatterns = [
    path('info/', CartInfoView.as_view(), name='info'),
    path('cart_del/', DelCartView.as_view(), name='cart_del'),
]