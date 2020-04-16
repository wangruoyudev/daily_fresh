from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.http import HttpResponse


class GoodsDetailView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'goods/detail.html')
