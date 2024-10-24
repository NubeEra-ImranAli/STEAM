from django.urls import path
from teacher import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('create-student', views.create_student,name='create-student'),
    path('student-list', views.student_list,name='student-list'),
    path('student-list-pending', views.student_list_pending,name='student-list-pending'),
    path('uploadstud/', views.upload_student_csv, name='upload-student-csv'),

    path('modulequestion/', views.modulequestion_list, name='modulequestion_list'),
    path('modulequestion/create/', views.modulequestion_create, name='modulequestion_create'),
    path('modulequestion/update/<int:id>/', views.modulequestion_update, name='modulequestion_update'),
    path('modulequestion/delete/<int:id>/', views.modulequestion_delete, name='modulequestion_delete'),
]
