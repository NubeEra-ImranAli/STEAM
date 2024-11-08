from django.urls import path
from principle import views

urlpatterns = [

    path('create-teacher', views.create_teacher,name='create-teacher'),
    path('test-list', views.test_list,name='test-list'),
    path('teacher-list', views.teacher_list,name='teacher-list'),
    path('teacher-list-pending', views.teacher_list_pending,name='teacher-list-pending'),
    
]
