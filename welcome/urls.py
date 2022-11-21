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
    path('classes/search', views.search_classes, name='search'),
    path('update', views.update, name='update'),
    path('send_friend_request/<int:userID>/', views.send_friend_request, name='send friend request'),
    path('accept_friend_request/<int:requestID>/', views.accept_friend_request, name='accept friend request'),
    path('decline_friend_request/<int:requestID>/', views.decline_friend_request, name='decline friend request'),
    path('friends', views.friends, name='friends'),
    path('chat/', views.rooms, name='rooms'),
    path('chat/<str:room_name>', views.room, name='room'),
    path('updatetimes', views.updateTimes, name='updatetimes'),
    path('remove_friend/<int:userID>/', views.remove_friend, name='remove friend'),

]