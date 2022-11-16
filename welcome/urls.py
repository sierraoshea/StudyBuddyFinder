from django.urls import path, include
from django.contrib.auth.views import LogoutView

from welcome.views import search_classes
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view(), name='logout'),
    path('profile', views.EditView.as_view(), name='profile'),
    path('profile/edit_classes', views.edit_classes, name='classes'),
    path('profile/edit_classes/delete', views.delete_class, name='delete'),
    path('profile/edit_classes/add', views.add_classes, name='add'),
    path('profile/edit_classes/<str:subject>/', views.subject_view, name='class_view'),
    path('classes/search', views.search_classes, name ='search'),
    path('update', views.update, name='update'),
    path('updatetimes', views.updateTimes, name='updatetimes'),
    path('newmeeting/<int:reciever_id>', views.new_meeting, name='newmeeting'),
    path('newmeeting/<int:reciever_id>/submit', views.confirm_meeting, name='confmeeting')
]