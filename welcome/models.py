from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class UserClasses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=10)
    catalog_number = models.IntegerField()
    component = models.CharField(max_length=10)
    section = models.IntegerField()
    professor = models.CharField(max_length=200)
    available = models.BooleanField(default=False)
    search_class = models.CharField(max_length=100, default="")

    def __str__(self):
        if self.professor == "-":
            return self.subject + " " + str(self.catalog_number) + " " + self.component + " Section " + str(self.section)
        else:
            return self.subject + " " + str(self.catalog_number) + " " + self.component + " Section " + str(self.section) + " w/ " + self.professor

    def as_array(self):
        return [self.subject, self.catalog_number, self.component]


#class UserFriend(models.Model):
    #friends = models.ManyToManyField("User", blank=True)


class Friend_Request(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)

