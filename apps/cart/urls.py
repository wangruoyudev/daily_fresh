from django.urls import path
from .views import CartInfoView

app_name = 'cart'
urlpatterns = [
    path('info/', CartInfoView.as_view(), name='info'),
]