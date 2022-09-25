from django.http import HttpResponse


def index(request):
    return HttpResponse("Welcome to Group B-03's study buddy finder website!")