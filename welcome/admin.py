from django.contrib import admin
from .models import UserClasses
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Class
from .models import FriendList

class ClassesInline(admin.TabularInline):
    model = UserClasses
    extra = 5

class CustomUserAdmin(UserAdmin):
    inlines = [ClassesInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Class)
admin.site.register(FriendList)