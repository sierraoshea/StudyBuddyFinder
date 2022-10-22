from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view(), name='logout'),
    path('profile', views.EditView.as_view(), name='profile'),
    path('profile/edit_classes', views.edit_classes, name='classes'),
    path('profile/edit_classes/delete', views.delete_class, name='delete'),
    path('profile/edit_classes/add', views.add_classes, name='add'),
    path('',views.home,name='home')
]