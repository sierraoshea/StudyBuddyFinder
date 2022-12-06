from django.contrib import admin
from .models import UserClasses, UserToUserChat, Message
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Class
from .models import FriendList
from .models import Friend_Request
from .models import meeting

class ClassesInline(admin.TabularInline):
    model = UserClasses
    extra = 5

class CustomUserAdmin(UserAdmin):
    inlines = [ClassesInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Class)
admin.site.register(FriendList)
admin.site.register(Friend_Request)
admin.site.register(UserToUserChat)
admin.site.register(Message)
admin.site.register(meeting)
