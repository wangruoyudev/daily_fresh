from django.urls import path
from .views import CreateOrderView

app_name = 'order'
urlpatterns = [
    path('create_order/', CreateOrderView.as_view(), name='create_order'),
]