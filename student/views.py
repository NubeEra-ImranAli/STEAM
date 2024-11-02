from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from steamapp import models as MyModels
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Exists, OuterRef, Value, CharField, Case, When

# Display list of modules
@login_required
def studykit(request):
    if str(request.session['utype']) == 'student':
        # Create a subquery to check if the lesson has been watched
        watched_lessons_subquery = MyModels.LessonWatched.objects.filter(
            lesson=OuterRef('id'),
            student=request.user
        )
        has_question_subquery = MyModels.ModuleQuestion.objects.filter(
            module=OuterRef('module__id')
        )

        # Get the lessons for the user, including the watched_status
        lessons = list(MyModels.Lesson.objects.filter(
            module__grade__user__id=request.user.id,
            module__grade__user__grade_id=request.user.grade.id,
            module__grade__user__school_id=request.user.school.id,
            module__grade_id=request.user.grade.id
        ).distinct().annotate(
            watched_status=Exists(watched_lessons_subquery),  # Check if the lesson has been watched
            has_ques=Exists(has_question_subquery)
        ).values(
            'id', 
            'module__id', 
            'module__module_name', 
            'heading',
            'watched_status',  # Include watched_status in the values
            'has_ques'
        ).order_by('module__module_name', 'serialno'))

        # Set the watched status display
        for i, lesson in enumerate(lessons):
            if i == 0:  # First lesson in the list
                lesson['watched_status_display'] = 'YES'
            else:
                lesson['watched_status_display'] = 'YES' if lesson['watched_status'] else 'NO'
        total_lessons = MyModels.Lesson.objects.filter(
            module__grade__user__id=request.user.id,
            module__grade__user__grade_id=request.user.grade.id,
            module__grade__user__school_id=request.user.school.id,
            module__grade_id=request.user.grade.id
        ).count()

        # Count watched lessons from LessonWatched model
        watched_lessons = MyModels.LessonWatched.objects.filter(
            student=request.user,
            grade=request.user.grade
        ).count()

        watched_percentage = 0
        # Calculate the percentage of watched lessons
        if total_lessons > 0:  # Avoid division by zero
            watched_percentage = (watched_lessons / total_lessons) * 100
        
        from itertools import groupby
        from operator import itemgetter

        grouped_lessons = {key: list(group) for key, group in groupby(lessons, key=itemgetter('module__module_name'))}
        
        return render(request, 'student/studykit/studykit.html', 
                      {'grouped_lessons': grouped_lessons,
                       'total_lessons': total_lessons,
                       'watched_lessons': watched_lessons,
                       'watched_percentage':watched_percentage
                       })
    else:
        return render(request,'loginrelated/diffrentuser.html')

def get_module_questions(request, lesson_id):
    # Fetch questions based on the lesson_id or any criteria you need
    module_id = MyModels.Lesson.objects.filter(id=lesson_id).values('module_id')[0]['module_id']
    questions = MyModels.ModuleQuestion.objects.filter(module_id=module_id)  # Adjust filtering as needed
    questions_data = [{"id": q.id, "question": q.question,
                       "option1": q.option1,
                       "option2": q.option2,
                       "option3": q.option3,
                       "option4": q.option4,
                       
                       } for q in questions]
    
    return JsonResponse({"questions": questions_data})
# View to return full lesson details (for AJAX)
@login_required
def get_lesson_details(request, lesson_id):
    lesson = MyModels.Lesson.objects.filter(id=lesson_id).values(
        'about', 'reqmaterial', 'video', 'digram', 'code', 'process', 'get'
    ).first()

    student = request.user  # Assuming the user is logged in and is the student
    grade = student.grade  # Assuming the user model has a grade field
    module = MyModels.Lesson.objects.get(id=lesson_id).module  # Get the lesson's module
    # Create a LessonWatched instance
    MyModels.LessonWatched.objects.get_or_create(
        student=student,
        grade=grade,
        module=module,
        lesson_id=lesson_id
    )
    return JsonResponse(lesson)

@login_required
@csrf_exempt
def save_lesson_watched(request):
    if request.method == 'POST':
        lesson_id = request.POST.get('lesson_id')
        student = request.user
        
        # Get or create the LessonWatched entry
        lesson = MyModels.Lesson.objects.get(id=lesson_id)
        module = lesson.module
        MyModels.LessonWatched.objects.get_or_create(
            student=student,
            grade=student.grade,
            module=module,
            lesson=lesson
        )

        # Recalculate the progress
        total_lessons = MyModels.Lesson.objects.filter(
            module__grade__user__id=request.user.id,
            module__grade__user__grade_id=request.user.grade.id,
            module__grade__user__school_id=request.user.school.id,
            module__grade_id=request.user.grade.id
        ).count()

        watched_lessons = MyModels.LessonWatched.objects.filter(
            student=request.user,
            grade=request.user.grade
        ).count()

        watched_percentage = 0
        if total_lessons > 0:
            watched_percentage = (watched_lessons / total_lessons) * 100

        return JsonResponse({
            'success': True,
            'watched_percentage': watched_percentage,
            'watched_lessons': watched_lessons,
            'total_lessons': total_lessons
        })

    return JsonResponse({'success': False}, status=400)