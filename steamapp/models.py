from django.db import models
from django.db import models
import datetime

from django.contrib.auth.models import AbstractUser

class Grade(models.Model):
    # Example fields
    grade_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.grade_name

class School(models.Model):
    school_name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    enrollment_date = models.DateField(auto_now=True)
    def __str__(self):
        return self.school_name
    
class User(AbstractUser):
    school=models.ForeignKey(School,on_delete=models.SET_NULL, null=True)
    grade=models.ForeignKey(Grade,on_delete=models.SET_NULL, null=True)
    roll_no = models.CharField(max_length=200)
    user_full_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    CAT = (
        ("student", "student"),
    )
    utype = models.CharField(max_length=200, choices=CAT, default="student")
    mobile = models.CharField(max_length=10)
    whatsappno = models.CharField(max_length=10)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    profile_updated = models.BooleanField(default=False)
    status = models.BooleanField(default=False)

class UserLog(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL, null=True)
    login =  models.DateTimeField(default=datetime.datetime.now)
    logout = models.DateTimeField(default=datetime.datetime.now)
    dur = models.CharField(default='',max_length=200)
    session_id = models.CharField(default='',max_length=200)

    
class IsFirstLogIn(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.user

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=2048)
    method = models.CharField(max_length=16)
    status_code = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.user.username} accessed {self.url} ({self.status_code})'
    
class ErrorLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    url = models.CharField(max_length=2048)
    exception = models.TextField()
    traceback = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'Error occurred while processing {self.url}'

class LastUserLogin(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL, null=True)


    
