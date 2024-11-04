from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from steamapp import models as MyModels
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Exists, OuterRef,Case, When, Value, IntegerField,F
import json

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

        # Get all lessons with their watched_status
        lessons = list(MyModels.Lesson.objects.filter(
            module__grade__user__id=request.user.id,
            module__grade__user__grade_id=request.user.grade.id,
            module__grade__user__school_id=request.user.school.id,
            module__grade_id=request.user.grade.id
        ).distinct().annotate(
            watched_status=Exists(watched_lessons_subquery),
            has_ques=Exists(has_question_subquery)
        ).values(
            'id', 
            'module__id', 
            'module__module_name', 
            'heading',
            'watched_status',
            'has_ques'
        ).order_by('module__module_name', 'serialno'))
        
        # Iterate through the lessons and set the first NO to YES after the last YES
        found_first_no = False  # Flag to track if we've found the first NO

        for i, lesson in enumerate(lessons):
            if i == 0 and not lesson['watched_status']:  # First lesson in the list
                lesson['watched_status_display'] = 'YES'
                lesson['watched_status'] = True
            if lesson['watched_status']:  # If we encounter a YES
                found_first_no = True  # Allow subsequent NOs to be changed to YES
                lesson['watched_status_display'] = 'YES'
            elif found_first_no and not lesson['watched_status']:  # If we encounter the first NO after a YES
                lesson['watched_status'] = True  # Change the first NO to YES
                lesson['watched_status_display'] = 'YES'
                break  # Exit after changing the first NO


        
        
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

@login_required
def get_module_questions(request, lesson_id):
    # Fetch questions based on the lesson_id or any criteria you need
    module_id = MyModels.Lesson.objects.filter(id=lesson_id).values('module_id')[0]['module_id']
    questions = MyModels.ModuleQuestion.objects.filter(module_id=module_id).order_by('?')  # Adjust filtering as needed
    questions_data = [{"id": q.id, "question": q.question,
                       "option1": q.option1,
                       "option2": q.option2,
                       "option3": q.option3,
                       "option4": q.option4,
                       "answer": q.answer,
                       "module_id":module_id,
                       "grade_id":q.grade_id,
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
    a = MyModels.LessonWatched.objects.get_or_create(
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

@csrf_exempt
def submit_quiz_results(request):
    if request.method == 'POST':
        try:
            # Load the JSON data from the request
            data = json.loads(request.body)
            results = []

            total_correct = 0
            total_questions = len(data)
            total_marks = 0
            
            module_id = data[0]['moduleID']  # Get the first moduleID
            grade_id = data[0]['gradeID']      # Get the first gradeID
            saveresult = MyModels.ModuleResult.objects.create(
                student_id = request.user.id,
                grade_id = grade_id,
                module_id = module_id,
                marks = 0,
                wrong = 0,
                correct =0
            )
            saveresult.save()
            # Process each submitted answer
            for result in data:
                question_id = result.get('questionID')
                given_answer = result.get('givenAnswer')
                if given_answer == None:
                    given_answer= 'Not Attempted'
                # Fetch the question from the database
                question = MyModels.ModuleQuestion.objects.filter(id=question_id).first()
                
                if question:
                    saveresultdet = MyModels.ModuleResultDetails.objects.create(
                        moduleresult = saveresult,
                        question = question,
                        selected = given_answer
                    )
                    saveresultdet.save()
                    # Check if the given answer matches the correct answer
                    if given_answer == question.answer:
                        total_correct += 1
                        total_marks += question.marks
                        results.append({
                            'questionID': question.question,
                            'givenAnswer': given_answer,
                            'result': 'Correct'
                        })
                    else:
                        results.append({
                            'questionID': question.question,
                            'givenAnswer': given_answer,
                            'result': 'Incorrect'
                        })
                else:
                    results.append({
                        'questionID': question.question,
                        'givenAnswer': given_answer,
                        'result': 'Question not found'
                    })
            # Calculate the percentage of correct answers
            if total_questions > 0:
                percentage = (total_correct / total_questions) * 100
            else:
                percentage = 0  # Handle division by zero if no questions

            # Prepare the response data
            saveresult.wrong = total_questions - total_correct
            saveresult.correct = total_correct
            saveresult.marks = total_marks
            saveresult.save()
            response_data = {
                'status': 'success',
                'totalCorrect': total_correct,
                'totalQuestions': total_questions,
                'percentage': round(percentage, 2),  # Round to 2 decimal places
                'results': results
            }

            return JsonResponse(response_data, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed.'}, status=405)


@login_required
def module_exams(request):
    if str(request.session['utype']) == 'student':
        modules = MyModels.ModuleResult.objects.filter(student_id=request.user.id,grade_id = request.user.grade_id ).values(
        'module__module_name','module__id'
    ).distinct()
        return render(request, 'student/studykit/exam_modules.html', 
                      {'modules': modules
                       })
    else:
        return render(request,'loginrelated/diffrentuser.html')

@login_required
def show_module_exams_attemps(request,module_id):
    if str(request.session['utype']) == 'student':
        modules = MyModels.ModuleResult.objects.filter(module_id= module_id, student_id=request.user.id,grade_id = request.user.grade_id ).values(
        'module__module_name','module__id','marks','wrong','correct','date','id'
    )
        return render(request, 'student/studykit/show_exam_modules_attempt.html', 
                      {'modules': modules
                       })
    else:
        return render(request,'loginrelated/diffrentuser.html')
    
@login_required
def show_module_result(request,result_id):
    if str(request.session['utype']) == 'student':
        results = (
        MyModels.ModuleResultDetails.objects
        .filter(moduleresult_id=result_id)
        .select_related('question')  # Use select_related to optimize the join
        .annotate(
            marks=Case(
                When(question__answer=F('selected'), then=F('question__marks')),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
        .distinct()
        .values(
            'question__question',
            'question__option1',
            'question__option2',
            'question__option3',
            'question__option4',
            'selected',
            'question__answer',
            'marks'
        )
    )
        return render(request, 'student/studykit/show_exam_modules_result.html', 
                      {'results': results
                       })
    else:
        return render(request,'loginrelated/diffrentuser.html')