from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def cart_index(request):
    return HttpResponse('cart_index')
