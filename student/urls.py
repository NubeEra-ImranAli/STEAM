from django.urls import path
from student import views

urlpatterns = [
    path('studykit/', views.studykit, name='studykit'),
    path('save_lesson_watched/', views.save_lesson_watched, name='save_lesson_watched'),
    path('get-lesson-details/<int:lesson_id>/', views.get_lesson_details, name='get-lesson-details'),
    path('get-module-questions/<int:lesson_id>/',  views.get_module_questions, name='get-module-questions'),
    path('submit-quiz/', views.submit_quiz_results, name='submit-quiz'),
    path('module-exams/', views.module_exams, name='module-exams'),
    path('show-module-exams-attempts/<int:module_id>/', views.show_module_exams_attemps, name='show-module-exams-attempts'),
    path('show-module-result/<int:result_id>/', views.show_module_result, name='show-module-result'),
]
