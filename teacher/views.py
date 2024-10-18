from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
import random
from django.contrib import messages
from steamapp import models as MyModels
from steamapp.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from steamapp.models import User
from django.db import IntegrityError
from steamapp.views import check_username
import csv
def roman_to_int(roman):
    roman_values = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000
    }
    prev_value = 0
    total = 0
    for char in reversed(roman):
        value = roman_values[char]
        if value < prev_value:
            total -= value
        else:
            total += value
        prev_value = value
    return total

def student_list(request):
    if str(request.session['utype']) == 'teacher':
        query = request.GET.get('search', '')
        users = User.objects.all().filter(utype = 'student', school_id = request.user.school.id, status = True)
        if query:
                users = users.filter(
                    Q(first_name__icontains=query) |
                    Q(last_name__icontains=query) |
                    Q(username__icontains=query)
                )
        paginator = Paginator(users, 12)  # Show 10 users per page
        page_number = request.GET.get('page')
        users_paginated = paginator.get_page(page_number)
        
        return render(request,'teacher/user/student_list.html',{'users':users_paginated})
    else:
        return render(request,'loginrelated/diffrentuser.html')
    
def student_list_pending(request):
    if str(request.session['utype']) == 'teacher':
        query = request.GET.get('search', '')
        users = User.objects.all().filter(utype = 'student', school_id = request.user.school.id, status = False)
        if query:
                users = users.filter(
                    Q(first_name__icontains=query) |
                    Q(last_name__icontains=query) |
                    Q(username__icontains=query)
                )
        paginator = Paginator(users, 12)  # Show 10 users per page
        page_number = request.GET.get('page')
        users_paginated = paginator.get_page(page_number)
        
        return render(request,'teacher/user/student_list_pending.html',{'users':users_paginated})
    else:
        return render(request,'loginrelated/diffrentuser.html')
    
def create_student(request):
    if str(request.session['utype']) == 'teacher':

        if request.method == "POST":
            # Get form data
            username = request.POST['username'].strip()
            grade = request.POST['grade'].strip()
            division = request.POST['division'].strip()
            roll_no = request.POST['roll_no'].strip()
            password = 'steam123'
            
            # Create user
            try:
                newuser = User.objects.create_user(
                    username=username,
                    password=password,
                    utype = 'student',
                    school_id = request.user.school.id,
                    grade_id = grade,
                    division_id = division,
                    roll_no = roll_no,
                )

                newuser.save()
                return redirect('student-list-pending')
                
            except IntegrityError:
                return HttpResponse("A user with that username already exists.")
            except Exception as e:
                return HttpResponse(f"Something went wrong: {e}")
        divisions = MyModels.Division.objects.all().order_by('division_name')                
        # Fetch all grades
        grades = list(MyModels.Grade.objects.all())

        # Sort grades using the custom roman_to_int function
        grades_sorted = sorted(grades, key=lambda grade: roman_to_int(grade.grade_name))                
        return render(request, 'teacher/user/create_student.html', {'grades': grades_sorted, 'divisions': divisions})
    else:
        return render(request,'loginrelated/diffrentuser.html')
    
def check_username_exist(request, username, fname, lname):
    # Check if the provided username exists
    if User.objects.filter(username=username).exists():
        # Username exists, so generate a new one
        while True:
            # Generate a random 4-digit number and create a new username
            random_number = random.randint(1000, 9999)
            new_username = f"{fname}_{lname}_{random_number}"
            
            # Check if the newly generated username exists
            if not User.objects.filter(username=new_username).exists():
                return new_username  # Unique username found, return it

    # Username does not exist, it's available
    return username


@login_required
def upload_student_csv(request):
    if str(request.session['utype']) == 'teacher':
        if request.method == 'POST':
            if 'select_file' not in request.FILES or request.FILES['select_file'] == '':
                messages.info(request, 'Please select a CSV file for upload')
            else:
                csv_file = request.FILES['select_file']

                # Check if file is CSV
                if not csv_file.name.endswith('.csv'):
                    messages.error(request, 'File is not CSV type')
                    return render(request, 'teacher/user/upload_user_csv.html')

                school = request.user.school.id
                file_data = csv_file.read().decode('utf-8').splitlines()

                csv_reader = csv.reader(file_data)
                next(csv_reader)  # Skip header row

                oldgr = ''
                olddiv = ''
                grid = 0
                divid = 0
                for row in csv_reader:
                    if len(row) != 5:
                        continue  # Skip row if it doesn't have expected 5 fields
                    fname, lname, grade, division, rollno = [col.strip() for col in row]

                    # Fetch or create Grade
                    if grade != oldgr:
                        oldgr = grade
                        gr, created = MyModels.Grade.objects.get_or_create(grade_name=oldgr)
                        grid = gr.id

                    # Fetch or create Division
                    if division != olddiv:
                        olddiv = division
                        dv, created = MyModels.Division.objects.get_or_create(division_name=olddiv)
                        divid = dv.id

                    # Ensure username is unique
                    username = fname + '_' + lname
                    username = check_username_exist(request, username, fname, lname)

                    # Create new User object
                    newuser = User.objects.create_user(
                        first_name=fname,
                        last_name=lname,
                        username=username,
                        password='steam123',
                        school_id=school,
                        grade_id=grid,
                        division_id=divid,
                        roll_no=rollno
                    )
                    newuser.save()  # Corrected to call the save method

                messages.success(request, 'CSV upload successful')
        return render(request, 'teacher/user/upload_student_csv.html')
    else:
        return render(request, 'loginrelated/diffrentuser.html')
@login_required
def teacher_view_user_list_view(request):
    #try:    
        if str(request.session['utype']) == 'teacher':
            query = request.GET.get('search', '')
            users = User.objects.all().filter(is_superuser = False, utype = 'student')

            if query:
                users = users.filter(
                    Q(first_name__icontains=query) |
                    Q(last_name__icontains=query) |
                    Q(username__icontains=query)
                )

            # Pagination
            paginator = Paginator(users, 12)  # Show 10 users per page
            page_number = request.GET.get('page')
            users_paginated = paginator.get_page(page_number)
            return render(request,'teacher/studentrelated/teacher_view_user_list.html',{'users': users_paginated, 'query': query})
    #except:
        return render(request,'loginrelated/diffrentuser.html')

    