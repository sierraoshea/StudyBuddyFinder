from django.db import models
from django.contrib.auth.models import User

class UserClasses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=10)
    catalog_number = models.IntegerField()
    component = models.CharField(max_length=10)

    def __str__(self):
        return self.subject + " " + str(self.catalog_number)
