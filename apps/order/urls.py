from django.urls import path
from .views import CreateOrderView, SubmitOrderView, AliPayView, QueryTradeStatus

app_name = 'order'
urlpatterns = [
    path('create_order/', CreateOrderView.as_view(), name='create_order'),
    path('submit_order/', SubmitOrderView.as_view(), name='submit_order'),
    path('pay_order/', AliPayView.as_view(), name='pay_order'),
    path('query_order/', QueryTradeStatus.as_view(), name='query_order'),
]