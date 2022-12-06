from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class UserClasses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=10)
    catalog_number = models.IntegerField()
    component = models.CharField(max_length=10)
    section = models.IntegerField()
    professor = models.CharField(max_length=200)
    available = models.BooleanField(default=False)
    description = models.CharField(max_length=200)

    def __str__(self):
        if self.professor == "-":
            return self.subject + " " + str(self.catalog_number) + " " + self.component + " Section " + str(self.section)
        else:
            return self.subject + " " + str(self.catalog_number) + " " + self.component + " Section " + str(self.section) + " w/ " + self.professor

    def as_array(self):
        return [self.subject, self.catalog_number, self.component]


class FriendList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user")
    friends = models.ManyToManyField(User, blank=True)


class Friend_Request(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)


class Class(models.Model):
    Name = models.CharField(max_length=150)
    Proffessor = models.CharField(max_length=150)
    students = models.ManyToManyField(User ,related_name = 'classes')


class UserToUserChat(models.Model):
    user1 = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name = 'user1')
    user2 = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name = 'user2')
    roomName = models.CharField(max_length=128, unique=True)


class Day(models.Model):
    day = models.CharField(max_length=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Time(models.Model):
    available = models.BooleanField(default =False)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    time = models.CharField(max_length = 10)

class Message(models.Model):
    room = models.ForeignKey(UserToUserChat, related_name='chat', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)

class Bio(models.Model):
    content = models.TextField()
    student = models.OneToOneField(User, on_delete=models.CASCADE)


class meeting(models.Model):
    date = models.DateField()
    time = models.TimeField()
    title = models.CharField(max_length=150)
    participants = models.ManyToManyField(User, related_name='meetings')


