from django.urls import path
from . import views

app_name = 'cart'
urlpatterns = [
    path('index', views.cart_index, name='index')
]