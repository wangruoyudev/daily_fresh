from django.urls import path, re_path
from .views import LoginView, RegisterView, ActiveAccount

app_name = 'user'
urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('register', RegisterView.as_view(), name='register'),
    re_path(r'^active_account/(?P<token>.*)/?$', ActiveAccount.as_view(), name='active_account'),
]