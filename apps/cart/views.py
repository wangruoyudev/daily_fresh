from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django_redis import get_redis_connection
# Create your views here.


class CartInfoView(LoginRequiredMixin, View):
    def get(self, request):
        con = get_redis_connection('default')
        cart_key = 'cart_id%s' % request.user.id
        cart_list = con.hgetall(cart_key)
        print('====>cart_list:', cart_list)
        context = {
        }
        return render(request, 'cart/cart.html', context)