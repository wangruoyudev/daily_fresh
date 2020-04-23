from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
# Create your views here.


class CreateOrderView(LoginRequiredMixin, View):
    def post(self, request):
        print('====>CreateOrderView-post:', request.POST)
        context = {}
        return render(request, 'order/place_order.html', context)

