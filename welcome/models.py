from django.db import models
from django.contrib.auth.models import User

class UserClasses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=10)
    catalog_number = models.IntegerField()
    component = models.CharField(max_length=10)
    section = models.IntegerField()
    professor = models.CharField(max_length=200)
    available = models.BooleanField(default=False)

    def __str__(self):
        if self.professor == "-":
            return self.subject + " " + str(self.catalog_number) + " " + self.component + " Section " + str(self.section)
        else:
            return self.subject + " " + str(self.catalog_number) + " " + self.component + " Section " + str(self.section) + " w/ " + self.professor

    def as_array(self):
        return [self.subject, self.catalog_number, self.component]

class Class(models.Model):
    Name = models.CharField(max_length=150)
    Proffessor = models.CharField(max_length=150)
    students = models.ManyToManyField(User ,related_name = 'classes')

class Day(models.Model):
    day = models.CharField(max_length=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Time(models.Model):
    available = models.BooleanField(default =False)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    time = models.CharField(max_length = 10)

    
        

