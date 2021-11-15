from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'product/index.html')


def about(request):
    return render(request, 'product/about.html')
