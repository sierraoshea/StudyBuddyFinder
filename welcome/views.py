from django.views import generic
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User

def index(request):
    if request.user.is_authenticated:
        first_initial = request.user.username[0].upper()
    else:
        first_initial = ""
    return render(request, 'welcome/index.html', {'first_initial': first_initial})

def signup(request):
    return render(request, 'welcome/signup.html')
    
