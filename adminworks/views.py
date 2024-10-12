from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from steamapp import models as MyModels
from django.contrib import messages
from steamapp.models import User
import random

# Display list of schools
@login_required
def school_list(request):
    schools = MyModels.School.objects.all()
    return render(request, 'adminworks/school/school_list.html', {'schools': schools})

# Create a new school
@login_required
def school_create(request):
    if request.method == 'POST':
        school_name = request.POST.get('school_name')
        contact_person = request.POST.get('contact_person')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')

        if school_name:
            MyModels.School.objects.create(
                                            school_name=school_name,
                                            contact_person=contact_person,
                                            email=email,
                                            address=address,
                                            phone_number=phone_number
                                            )
            messages.success(request, 'School created successfully!')
            return redirect('school_create')
    return render(request, 'adminworks/school/school_create.html')

# Update an existing school
@login_required
def school_update(request, id):
    school = get_object_or_404(MyModels.School, id=id)
    if request.method == 'POST':
        school_name = request.POST.get('school_name')
        contact_person = request.POST.get('contact_person')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        if school_name:
            school.school_name = school_name
            school.contact_person = contact_person
            school.email = email
            school.address = address
            school.phone_number = phone_number
            school.save()
            return redirect('school_list')
    return render(request, 'adminworks/school/school_update.html', {'school': school})

# Delete a school
@login_required
def school_delete(request, id):
    school = get_object_or_404(MyModels.School, id=id)
    school.delete()
    return redirect('school_list')

# Display list of grades
@login_required
def grade_list(request):
    grades = MyModels.Grade.objects.all()
    return render(request, 'adminworks/grade/grade_list.html', {'grades': grades})

# Create a new grade
@login_required
def grade_create(request):
    if request.method == 'POST':
        grade_name = request.POST.get('grade_name')
        if grade_name:
            MyModels.Grade.objects.create(grade_name=grade_name)
            messages.success(request, 'Grade created successfully!')
            return redirect('grade_create')
    return render(request, 'adminworks/grade/grade_create.html')

# Update an existing grade
@login_required
def grade_update(request, id):
    grade = get_object_or_404(MyModels.Grade, id=id)
    if request.method == 'POST':
        grade_name = request.POST.get('grade_name')
        if grade_name:
            grade.grade_name = grade_name
            grade.save()
            return redirect('grade_list')
    return render(request, 'adminworks/grade/grade_update.html', {'grade': grade})

# Delete a grade
@login_required
def grade_delete(request, id):
    grade = get_object_or_404(MyModels.Grade, id=id)
    grade.delete()
    return redirect('grade_list')

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

def check_username(request, username, fname, lname):
    # Check if the provided username exists
    if User.objects.filter(username=username).exists():
        # Username exists, so generate a new one
        new_username = None
        while True:
            # Generate a random 4-digit number and create a new username
            random_number = random.randint(1000, 9999)
            new_username = f"{fname}_{lname}_{random_number}"
            
            # Check if the newly generated username exists
            if not User.objects.filter(username=new_username).exists():
                break  # Unique username found, break the loop

        # Return the newly generated unique username
        return  new_username

    # Username does not exist, it's available
    return username

@login_required
def upload_student_csv(request):
    if str(request.session['utype']) == 'admin':
        if request.method=='POST':
            if request.POST.get('select_file') == '':
                messages.info(request, 'Please select CSV file for upload')
            else:
                csv_file = request.FILES["select_file"]
                school = request.POST.get('school')
                grade = request.POST.get('grade')
                file_data = csv_file.read().decode("utf-8")		
                lines = file_data.split("\n")
                
                no = 0
                for line in lines:						
                    no = no + 1
                    if no > 1:
                        fields = line.split(",")
                        fname = str(fields[0]).replace('///',',').replace('\r','')
                        lname = str(fields[1]).replace('///',',').replace('\r','')
                        rollno = str(fields[2]).replace('///',',').replace('\r','')
                        username = fname + '_' + lname
                        username = check_username(request,username,fname,lname)
                        newuser = User.objects.create_user(
                            first_name=fname,
                            last_name=lname,
                            username=username,
                            password='steam123',
                            school_id = school,
                            grade_id = grade
                        )
                        newuser.save

        schools = MyModels.School.objects.all().order_by('school_name')                
        # Fetch all grades
        grades = list(MyModels.Grade.objects.all())

        # Sort grades using the custom roman_to_int function
        grades_sorted = sorted(grades, key=lambda grade: roman_to_int(grade.grade_name))                
        return render(request,'adminworks/users/upload_user_csv.html', {'schools': schools,'grades': grades_sorted})

