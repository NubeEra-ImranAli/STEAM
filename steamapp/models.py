from django.db import models
from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
class Grade(models.Model):
    # Example fields
    grade_name = models.CharField(max_length=100)
    def __str__(self):
        return self.grade_name
    
class Division(models.Model):
    # Example fields
    division_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.division_name

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
    division=models.ForeignKey(Division,on_delete=models.SET_NULL, null=True)
    roll_no = models.CharField(max_length=200)
    user_full_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    CAT = (
        ("principle", "principle"),
        ("teacher", "teacher"),
        ("student", "student"),
    )
    utype = models.CharField(max_length=200, choices=CAT, default="student")
    mobile = models.CharField(max_length=10)
    whatsappno = models.CharField(max_length=10)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    profile_updated = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    created =  models.DateTimeField(default=timezone.now)


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

class Module(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)
    module_name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000,default='')
    module_pic = models.ImageField(upload_to='module_pic/', blank=True, null=True)
    def __str__(self):
        return self.module_name
    
class Lesson(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True)
    serialno = models.PositiveIntegerField()
    heading = RichTextField(default='')
    about = RichTextField(default='')
    reqmaterial =RichTextField(default='')
    video = models.CharField(max_length=1000,default='')
    digram = models.CharField(max_length=1000,default='')
    code = models.CharField(max_length=1000,default='')
    process = RichTextField(default='')
    get = RichTextField(default='')
    
    def __str__(self):
        return self.heading