from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from steamapp import models
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from steamapp.models import User
from django.db import IntegrityError

def test_list(request):
    if str(request.session['utype']) == 'principle':
        return render(request,'principle/test.html')
    else:
        return render(request,'loginrelated/diffrentuser.html')


def teacher_list(request):
    if str(request.session['utype']) == 'principle':
        users = User.objects.all().filter(utype = 'teacher', school_id = request.user.school.id, status = True)
        return render(request,'principle/user/teacher_list.html',{'users':users})
    else:
        return render(request,'loginrelated/diffrentuser.html')
    
def teacher_list_pending(request):
    if str(request.session['utype']) == 'principle':
        users = User.objects.all().filter(utype = 'teacher', school_id = request.user.school.id, status = False)
        return render(request,'principle/user/teacher_list_pending.html',{'users':users})
    else:
        return render(request,'loginrelated/diffrentuser.html')
    
def create_teacher(request):
    if str(request.session['utype']) == 'principle':

        if request.method == "POST":
            # Get form data
            username = request.POST['username'].strip()
            password = 'steam123'
            
            # Create user
            try:
                newuser = User.objects.create_user(
                    username=username,
                    password=password,
                    utype = 'teacher',
                    school_id = request.user.school.id,
                )

                newuser.save()
                return redirect('teacher-list')
                
            except IntegrityError:
                return HttpResponse("A user with that username already exists.")
            except Exception as e:
                return HttpResponse(f"Something went wrong: {e}")
        return render(request, 'principle/user/create_teacher.html')
    else:
        return render(request,'loginrelated/diffrentuser.html')
    