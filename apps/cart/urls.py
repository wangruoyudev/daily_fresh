from django.urls import path
from .views import CartInfoView, DelCartView, UpdateCartView

app_name = 'cart'
urlpatterns = [
    path('info/', CartInfoView.as_view(), name='info'),
    path('cart_del/', DelCartView.as_view(), name='cart_del'),
    path('update/', UpdateCartView.as_view(), name='update'),
]