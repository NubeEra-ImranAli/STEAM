from django.urls import path
from student import views

urlpatterns = [
    path('studykit/', views.studykit, name='studykit'),
    path('save_lesson_watched/', views.save_lesson_watched, name='save_lesson_watched'),
    path('get-lesson-details/<int:lesson_id>/', views.get_lesson_details, name='get-lesson-details'),

    
]
