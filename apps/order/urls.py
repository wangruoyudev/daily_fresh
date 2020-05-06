from django.urls import path, re_path
from .views import CreateOrderView, SubmitOrderView, AliPayView, QueryTradeStatus, OrderEvaluate

app_name = 'order'
urlpatterns = [
    path('create_order/', CreateOrderView.as_view(), name='create_order'),
    path('submit_order/', SubmitOrderView.as_view(), name='submit_order'),
    path('pay_order/', AliPayView.as_view(), name='pay_order'),
    path('query_order/', QueryTradeStatus.as_view(), name='query_order'),
    re_path(r'^evaluate_order/(?P<order_id>\d+)/?', OrderEvaluate.as_view(), name='evaluate_order'),
]