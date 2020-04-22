from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
# Create your views here.


class CreateOrderView(LoginRequiredMixin, View):
    def get(self, request):
        context = {}
        return render(request, 'order/place_order.html', context)

