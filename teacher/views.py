from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
import random
from django.contrib import messages
from steamapp import models as MyModels
from django.core.paginator import Paginator
from django.http import HttpResponse
from steamapp.models import User
from django.db import IntegrityError
import csv
from django.http import JsonResponse
from django.db.models import Sum, F, Value, Q, Count, F, Case, When, IntegerField
from django.db.models.functions import Coalesce
from datetime import datetime
import json
ROMAN_NUMERAL_MAP = {
                        'V': 5,
                        'VI': 6,
                        'VII': 7,
                        'VIII': 8,
                        'IX': 9,
                        'X': 10,
                    }
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
    
@login_required
def student_list(request):
    if str(request.session['utype']) == 'teacher':
        # Get the 'search' and 'grade_id' parameters from the GET request
        query = request.GET.get('search', '')
        grade_id = request.GET.get('grade_id')
        division_id = request.GET.get('division_id')

        # Get all grades to populate the dropdown
        grades = MyModels.Grade.objects.all()

        # Get all division to populate the dropdown
        divisions = MyModels.Division.objects.all()

        # Filter students by 'student' type and the current teacher's school
        students = User.objects.filter(
            utype='student',
            school_id=request.user.school.id,
            status=True
        )

        # Apply search filter
        if query:
            students = students.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(username__icontains=query) |
                Q(grade__grade_name__icontains=query) |
                Q(division__division_name__icontains=query)
            )

        # Apply grade filter if a grade is selected
        if grade_id:
            students = students.filter(grade_id=grade_id)
        
        # Apply division filter if a grade is selected
        if division_id:
            students = students.filter(division_id=division_id)

        # Annotate the students queryset with progress data
        students_with_data = students.annotate(
            total_lessons=Count('grade__lesson', distinct=True),
            total_watched_lessons=Count('lessonwatched', distinct=True),
            watched_percentage=Case(
                When(total_lessons__gt=0, then=F('total_watched_lessons') * 100 / F('total_lessons')),
                default=0,
                output_field=IntegerField()
            )
        ).select_related('grade', 'division')

        # Paginate the results
        paginator = Paginator(students_with_data, 50)
        page_number = request.GET.get('page')
        students_paginated = paginator.get_page(page_number)

        return render(request, 'teacher/user/student_list.html', {
            'users': students_paginated,
            'grades': grades,  # Pass grades to the template for the dropdown
            'selected_grade': grade_id,  # Preserve the selected grade
            'divisions': divisions,  # Pass divisions to the template for the dropdown
            'selected_division': division_id,  # Preserve the selected division
            'query': query  # Preserve the search query
        })
    else:
        return render(request, 'loginrelated/diffrentuser.html')
    
def student_attendance(request):
    if str(request.session['utype']) == 'teacher':
        query = request.GET.get('search', '')
        grade_id = request.GET.get('grade_id', '')
        division_id = request.GET.get('division_id', '')

        # Filter students based on search criteria
        students = User.objects.all().filter(utype ='student',school_id = request.user.school_id,status=True)
        if query:
            students = students.filter(first_name__icontains=query) | students.filter(last_name__icontains=query)
        if grade_id:
            students = students.filter(grade_id=grade_id)
        if division_id:
            students = students.filter(division_id=division_id)
            
        # Handle POST request (for saving attendance)
        if request.method == 'POST':
            tdate_str = request.POST.get('tdate')

            # Parse the date (assume it's passed in the format dd-mm-yyyy)
            try:
                tdate = datetime.strptime(tdate_str, '%d-%m-%Y').date()
            except ValueError:
                return JsonResponse({"error": "Invalid date format"}, status=400)

            # Process each student's attendance
            for student in students:
                student_id = student.id
                attendance = request.POST.get(f'attendance_{student_id}')

                if attendance is not None:
                    # Convert attendance to integer (1 for present, 0 for absent)
                    is_present = int(attendance)
                    try:
                        attendance_record = MyModels.StudentAttendance.objects.get(
                            student_id=student.id, 
                            date=tdate
                        )
                        # If the attendance record exists, update it
                        attendance_record.status = is_present
                        attendance_record.save()

                    except MyModels.StudentAttendance.DoesNotExist:
                        # If the record doesn't exist, create it
                        attendance_record = MyModels.StudentAttendance(
                            student=student,
                            date=tdate,
                            status=is_present
                        )
                        attendance_record.save()
                    

            # Redirect to the same page or a success page after saving
            return redirect('student-attendance')  # You can change this to a success page URL if needed

        # If GET request, render the page with the student data
        return render(request, 'teacher/user/student_attendance.html', {
            'students': students,
            'tdate': datetime.today().strftime('%d-%m-%Y'),  # Default to today's date
            'query': query,
            'grades': MyModels.Grade.objects.all(),
            'divisions': MyModels.Division.objects.all(),
            'selected_grade': grade_id,
            'selected_division': division_id,
        })

    return render(request, 'loginrelated/diffrentuser.html')
    
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
        paginator = Paginator(users, 50)  # Show 10 users per page
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
                    fname, lname, grade, division, rollno = [col.strip() for col in row]

                    # Fetch or create Grade
                
                    gr , created = MyModels.Grade.objects.get_or_create(grade_name=grade)
                    grid = gr.id

                    # Fetch or create Division
                    
                    dv , created  = MyModels.Division.objects.get_or_create(division_name=division)
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
            paginator = Paginator(users, 50)  # Show 10 users per page
            page_number = request.GET.get('page')
            users_paginated = paginator.get_page(page_number)
            return render(request,'teacher/studentrelated/teacher_view_user_list.html',{'users': users_paginated, 'query': query})
    #except:
        return render(request,'loginrelated/diffrentuser.html')


def attendance_report_view(request):
    # Fetch all grades and divisions for the dropdown
    grades = MyModels.Grade.objects.all()
    divisions = MyModels.Division.objects.all()

    # Get search parameters from GET request
    search_date = request.GET.get('date', None)
    search_grade = request.GET.get('grade', None)
    search_division = request.GET.get('division', None)

    # Convert date from string to date object if provided
    if search_date:
        try:
            search_date = datetime.strptime(search_date, '%d-%m-%Y').date()
        except ValueError:
            search_date = None  # If invalid date format, ignore

    # Filter StudentAttendance based on the search date
    attendance_data = MyModels.StudentAttendance.objects.all()
    if search_date:
        attendance_data = attendance_data.filter(date=search_date)

    # Filter by grade and division if provided
    if search_grade:
        attendance_data = attendance_data.filter(student__grade__id=search_grade)
    if search_division:
        attendance_data = attendance_data.filter(student__division__id=search_division)

    # Get distinct grades and divisions from the filtered attendance data
    grades_and_divisions = attendance_data.values('student__grade', 'student__division') \
        .distinct()

    report = []

    for item in grades_and_divisions:
        grade = MyModels.Grade.objects.get(id =item['student__grade']) 
        division = MyModels.Division.objects.get(id =item['student__division']) 

        # Get the total number of students in this grade and division (from User model)
        total_students = User.objects.filter(grade=grade, division=division, utype='student',status=True).count()

        # Get the attendance data for these students (filtered by date)
        students_in_division = attendance_data.filter(student__grade=grade, student__division=division)

        # Count present and absent students based on attendance data
        total_present = students_in_division.filter(status=1).count()
        total_absent = students_in_division.filter(status=0).count()

        # Calculate attendance percentage
        if total_students > 0:
            attendance_percentage = (total_present / total_students) * 100
        else:
            attendance_percentage = 0

        # Prepare the report entry
        report.append({
            'Date': search_date.strftime('%d-%m-%Y') if search_date else '',
            'Grade': grade,
            'Division': division,
            'total_students': total_students,
            'total_present': total_present,
            'total_absent': total_absent,
            'attendance_percentage': round(attendance_percentage, 2),
        })
    # Pass data to the template
    return render(request, 'teacher/user/student_attendance_report.html', {
        'report': report,
        'search_date': search_date.strftime('%d-%m-%Y') if search_date else '',
        'search_grade': search_grade,
        'search_division': search_division,
        'grades': grades,
        'divisions': divisions,
    })


@login_required
def attendance_details(request, grade_id, division_id, date):
    if str(request.session['utype']) == 'teacher':
        # Convert the date string to a date object
        try:
            attendance_date = datetime.strptime(date, '%d-%m-%Y').date()
        except ValueError:
            return render(request, 'attendance/error.html', {'error': 'Invalid date format'})

        # Query to get students with the given grade, division, and attendance date
        students_with_attendance = (
            User.objects.filter(grade_id=grade_id, division_id=division_id, utype='student',status=True)
            .prefetch_related('studentattendance_set')  # Optimize query to access related attendance
        )

        # Get grade and division names
        grade_name = MyModels.Grade.objects.get(id=grade_id).grade_name
        division_name = MyModels.Division.objects.get(id=division_id).division_name

        # Prepare students' data with attendance status for the given date
        students_data = []
        for student in students_with_attendance:
            # Get the first attendance record for the specific date
            attendance = student.studentattendance_set.filter(date=attendance_date).first()

            # Determine the attendance status
            if attendance:
                if attendance.status == 1:
                    status = 'Present'
                elif attendance.status == 0:
                    status = 'Absent'
                else:
                    status = 'Unknown'
            else:
                status = 'No Record'

            students_data.append({
                'id': student.pk ,
                'user_full_name': student.first_name + ' ' + student.last_name,
                'roll_no': student.roll_no,
                'attendance_status': status
            })

        # Render the template with the list of students and attendance status
        return render(request, 'teacher/user/student_attendance_details.html', {
            'students_data': students_data,
            'attendance_date': attendance_date,
            'grade_name': grade_name,
            'division_name': division_name,
        })
    else:
        return render(request, 'loginrelated/diffrentuser.html')
    

# Display list of exams
@login_required
def exam_list(request):
    if str(request.session['utype']) == 'teacher':
        exams = MyModels.Exam.objects.all()
        return render(request, 'teacher/exam/exam_list.html', {'exams': exams})
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Display list of exams
@login_required
def exam_student_top(request,exam_id):
    if str(request.session['utype']) == 'teacher':
        # Get the top 10 students ordered by their marks in the most recent exam result
        students = MyModels.ExamResult.objects.filter(exam_id=exam_id,student__status=True).order_by('-marks')[:10].values(
            'student__user_full_name',  # Student's full name
            'marks',                    # Marks
            'exam__id',                  # Exam ID
            'student__id'                # Student ID
        )
        return render(request, 'teacher/exam/exam_student_top.html', {'students': students})
    else:
        return render(request,'loginrelated/diffrentuser.html')

@login_required
def exam_student_marks_list(request,exam_id):
    if str(request.session['utype']) == 'teacher':
        # Query to get all students with their exam marks, or 0 if no result exists
        students = User.objects.filter(utype='student',status=True).annotate(
    marks=Coalesce(
        F('examresult__marks'),
        Value(0)  # Default to 0 if no ExamResult exists
    ),
    student_id=F('id'),
    exam_id=Coalesce(F('examresult__exam_id'), Value(0))  # Ensure a fallback value
).filter(
    Q(examresult__exam_id=exam_id) | Q(examresult__isnull=True)
)
        return render(request, 'teacher/exam/exam_student_result.html', {'students': students})
    else:
        return render(request,'loginrelated/diffrentuser.html')
    
@login_required
def exam_student_details_list(request,exam_id,student_id):
    #try:    
        if str(request.session['utype']) == 'teacher':
            # Pre-fetch related ExamResult for each ExamResultDetail
            exams = MyModels.ExamResultDetails.objects.all().filter(
                examresult__student__status=True,
                examresult__student_id=student_id,
                examresult__exam_id=exam_id,
                question_id__in=MyModels.ExamQuestion.objects.all()
            ).select_related('examresult')  # This will fetch the related ExamResult
            return render(request,'teacher/exam/exam_student_details.html',{'exams':exams})
    #except:
        return render(request,'lxpapp/404page.html')
# Create a new exam
@login_required
def exam_create(request):
    if str(request.session['utype']) == 'teacher':
        if request.method == 'POST':
            grade = request.POST.get('grade')
            exam_name = request.POST['exam_name']
            description = request.POST['description']
            if exam_name:
                mode = MyModels.Exam.objects.create(grade_id=grade,exam_name=exam_name,description=description)
                mode.save()
                messages.success(request, 'Exam created successfully!')
                return redirect('exam_create')
        grade = MyModels.Grade.objects.filter(id__isnull=False)\
                        .values('id','grade_name')
        grade = sorted(
                            grade,
                            key=lambda x: (ROMAN_NUMERAL_MAP.get(x['grade_name'], 0))
                        )
        return render(request, 'teacher/exam/exam_create.html',{'grades':grade})
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Update an existing exam
@login_required
    
def exam_update(request, id):
    if str(request.session['utype']) == 'teacher':
        if request.method == 'POST':
            grade = request.POST.get('grade')
            exam_name = request.POST['exam_name']
            description = request.POST['description']
            
            mode = get_object_or_404(MyModels.Exam, id=id)
            mode.grade_id = grade
            mode.exam_name = exam_name
            mode.description = description
            
            mode.save()
            messages.success(request, 'Exam updated successfully!' if id else 'Exam created successfully!')
            return redirect('exam_list')

        # Load the exam details if updating
        exam = None
        exam = get_object_or_404(MyModels.Exam, id=id)

        grades = MyModels.Grade.objects.filter(id__isnull=False).values('id', 'grade_name')
        grades = sorted(grades, key=lambda x: (ROMAN_NUMERAL_MAP.get(x['grade_name'], 0)))

        return render(request, 'teacher/exam/exam_update.html', {
            'grades': grades,
            'exam': exam,
        })
    else:
        return render(request, 'loginrelated/diffrentuser.html')

# Delete a exam
@login_required
def exam_delete(request, id):
    if str(request.session['utype']) == 'teacher':
        exam = get_object_or_404(MyModels.Exam, id=id)
        exam.delete()
        
        return redirect('exam_list')
    else:
        return render(request,'loginrelated/diffrentuser.html')
    
def get_exams(request):
    grade_id = request.GET.get('grade_id')
    exams = MyModels.Exam.objects.filter(grade_id=grade_id).values('id', 'exam_name')
    return JsonResponse(list(exams), safe=False)    


# Display list of examquestion
@login_required
def examquestion_list(request):
    if str(request.session['utype']) == 'teacher':
        examquestion = MyModels.ExamQuestion.objects.all().order_by('grade', 'exam')
        return render(request, 'teacher/examquestion/examquestion_list.html', {'examquestion': examquestion})
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Create a new examquestion
@login_required
def examquestion_create(request):
    if str(request.session['utype']) == 'teacher':
        if request.method == 'POST':
            grade = request.POST.get('grade')
            exam = request.POST.get('exam')
            question = request.POST['question']
            option1 = request.POST['option1']
            option2 = request.POST['option2']
            option3 = request.POST['option3']
            option4 = request.POST['option4']
            answer = request.POST['answer']
            mode = MyModels.ExamQuestion.objects.create(grade_id=grade,
                                                  exam_id=exam,
                                                  question = question,
                                                  option1=option1,
                                                  option2=option2,
                                                  option3=option3,
                                                  option4=option4,
                                                  answer=answer,
                                                  marks=1
                                                  )
            mode.save()
            messages.success(request, 'ExamQuestion created successfully!')
            return redirect('examquestion_create')
        grade = MyModels.Grade.objects.filter(id__isnull=False)\
                        .values('id','grade_name')
        grade = sorted(
                            grade,
                            key=lambda x: (ROMAN_NUMERAL_MAP.get(x['grade_name'], 0))
                        )
        
        return render(request, 'teacher/examquestion/examquestion_create.html',{'grades':grade})
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Update an existing examquestion
@login_required
    
def examquestion_update(request, id):
    if str(request.session['utype']) == 'teacher':
        if request.method == 'POST':
            grade = request.POST.get('grade')
            exam = request.POST.get('exam')
            question = request.POST['question']
            option1 = request.POST['option1']
            option2 = request.POST['option2']
            option3 = request.POST['option3']
            option4 = request.POST['option4']
            answer = request.POST['answer']
            
            les = get_object_or_404(MyModels.ExamQuestion, id=id)
            les.grade_id = grade
            les.exam = exam
            les.question = question
            les.option1 = option1
            les.option2 = option2
            les.option3 = option3
            les.option4 = option4
            les.answer = answer
            les.save()
            messages.success(request, 'ExamQuestion updated successfully!' if id else 'ExamQuestion created successfully!')
            return redirect('examquestion_list')

        grades = MyModels.Grade.objects.filter(id__isnull=False).values('id', 'grade_name')
        grades = sorted(grades, key=lambda x: (ROMAN_NUMERAL_MAP.get(x['grade_name'], 0)))

        les = get_object_or_404(MyModels.ExamQuestion, id=id)
        grade = les.grade_id
        exam = les.exam_id
        question = les.question
        option1 = les.option1
        option2 =  les.option2 
        option3 = les.option3 
        option4 = les.option4
        answer = les.answer
        return render(request, 'teacher/examquestion/examquestion_update.html', {
            'grades': grades,
            'grade': grade,
            'exam': exam,
            'question' :question,
            'option1': option1,
            'option2': option2,
            'option3': option3,
            'option4': option4,
            'answer': answer,
        })
    else:
        return render(request, 'loginrelated/diffrentuser.html')

# Delete a examquestion
@login_required
def examquestion_delete(request, id):
    if str(request.session['utype']) == 'teacher':
        examquestion = get_object_or_404(MyModels.ExamQuestion, id=id)
        # Now delete the examquestion instance
        examquestion.delete()
        
        return redirect('examquestion_list')
    else:
        return render(request,'loginrelated/diffrentuser.html')

# List scheduler_calender
@login_required
def teacher_calender(request):
    # Get schedulers for the logged-in teacher and use Coalesce to replace None with 0 for status_sum
    schedulers = MyModels.Scheduler.objects.filter(
        teacher_id=request.user.id
    ).annotate(
        status_sum=Coalesce(Sum('schedulerstatus__status'), Value(0))
    )
    return render(request, 'teacher/scheduler/teacher_calender.html', {'schedulers': schedulers})

# Display list of schedulerstatus
@login_required
def schedulerstatus_list(request):
    if str(request.session['utype']) == 'teacher':
        schedulerstatus = MyModels.SchedulerStatus.objects.all()
        return render(request, 'teacher/schedulerstatus/schedulerstatus_list.html', {'schedulerstatus': schedulerstatus})
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Create a new schedulerstatus
@login_required
def schedulerstatus_create(request):
    if str(request.session['utype']) == 'teacher':
        if request.method == 'POST':
            scheduler = request.POST.get('scheduler')
            status = request.POST.get('status')
            tdate_str = request.POST.get('tdate')
            status_sum = MyModels.SchedulerStatus.objects.filter(scheduler_id = scheduler).aggregate(Sum('status'))['status__sum']
            value = status
            if status_sum:
                if (float(status) < float(status_sum)) :
                    messages.warning(request, 'Scheduler Status count should be greater then Previous, total is ' + str(status_sum))
                    return redirect('schedulerstatus_create')
                value = float(status) - float(status_sum)
                if value > 100:
                    messages.warning(request, 'Scheduler Status count getting more then 100. Previous total is ' + str(status_sum))
                    return redirect('schedulerstatus_create') 
                if value == 0:
                    messages.warning(request, 'Scheduler Status count already marked as completed.' )
                    return redirect('schedulerstatus_create') 
            try:
                tdate = datetime.strptime(tdate_str, '%d-%m-%Y').date()
            except ValueError:
                return JsonResponse({"error": "Invalid date format"}, status=400)
           
            mode = MyModels.SchedulerStatus.objects.create(scheduler_id=scheduler,
                                                           teacher_id = request.user.id,
                                                  status=value,
                                                  date = tdate
                                                  )
            mode.save()
            messages.success(request, 'Scheduler Status created successfully!')
            return redirect('schedulerstatus_create')
        schedulers = MyModels.Scheduler.objects.filter(teacher_id = request.user.id)
        
        return render(request, 'teacher/schedulerstatus/schedulerstatus_create.html',{'schedulers':schedulers})
    else:
        return render(request,'loginrelated/diffrentuser.html')

@login_required
def get_scheduler_status_sum(request):
    # Check if the request is AJAX using the appropriate header
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        scheduler_id = request.GET.get("scheduler_id")
        
        # Get the sum of 'status' values for the given scheduler
        status_sum = MyModels.SchedulerStatus.objects.filter(scheduler_id=scheduler_id).aggregate(Sum('status'))['status__sum']
        
        # If no statuses exist, set sum to 0
        if status_sum is None:
            status_sum = 0

        # Log the status_sum for debugging (you can remove this in production)
        print(f"Scheduler ID: {scheduler_id}, Status Sum: {status_sum}")  # Add print statement to check
        
        return JsonResponse({"status_sum": status_sum})

    return JsonResponse({"error": "Invalid request"}, status=400)
# Delete a schedulerstatus
@login_required
def schedulerstatus_delete(request, id):
    if str(request.session['utype']) == 'teacher':
        schedulerstatus = get_object_or_404(MyModels.SchedulerStatus, id=id)
        # Now delete the schedulerstatus instance
        schedulerstatus.delete()
        
        return redirect('schedulerstatus_list')
    else:
        return render(request,'loginrelated/diffrentuser.html')