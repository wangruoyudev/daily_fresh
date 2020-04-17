"""daily_fresh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include
from apps.goods.views import IndexView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')), # 富文本编辑器
    path('cart/', include('cart.urls')),
    path('goods/', include('goods.urls')),
    path('order/', include('order.urls')),
    path('user/', include('user.urls')),
    re_path(r'^/?$', IndexView.as_view()),
]
