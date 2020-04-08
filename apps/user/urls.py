from django.urls import path, re_path
from .views import LoginView, RegisterView, ActiveAccount, \
    IndexView, TestView,UserInfo, UserOrder, UserAddress, userinfo, LogoutView

app_name = 'user'
urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('register', RegisterView.as_view(), name='register'),
    re_path(r'^active_account/(?P<token>.*)/?$', ActiveAccount.as_view(), name='active_account'),
    path('index', IndexView.as_view(), name='index'),
    path('', UserInfo.as_view(), name='info'),
    # path('', userinfo, name='info'),
    path('order', UserOrder.as_view(), name='order'),
    path('address', UserAddress.as_view(), name='address'),
    path('test', TestView.as_view(), name='test'),

]