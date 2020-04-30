from django.urls import path, re_path
from .views import LoginView, RegisterView, ActiveAccount, \
    TestView,UserInfo, UserOrder, UserAddress, userinfo, LogoutView, SetDefaultAddress

app_name = 'user'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    re_path(r'^active_account/(?P<token>.*)/?$', ActiveAccount.as_view(), name='active_account'),
    path('', UserInfo.as_view(), name='info'),
    # path('', userinfo, name='info'),
    re_path(r'^order/(?P<page_num>\d+)/', UserOrder.as_view(), name='order'),
    path('address/', UserAddress.as_view(), name='address'),
    path('address/set_default/', SetDefaultAddress.as_view(), name='set_default'),
    path('test/', TestView.as_view(), name='test'),

]