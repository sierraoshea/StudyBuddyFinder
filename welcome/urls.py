from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'Study Buddy Finder App'

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view(), name='logout'),
]