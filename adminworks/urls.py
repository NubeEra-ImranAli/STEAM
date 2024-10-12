from django.urls import path,include
from django.contrib import admin
from adminworks import views
from django.views.generic import TemplateView

urlpatterns = [
    path('schools/', views.school_list, name='school_list'),
    path('schools/create/', views.school_create, name='school_create'),
    path('schools/update/<int:id>/', views.school_update, name='school_update'),
    path('schools/delete/<int:id>/', views.school_delete, name='school_delete'),
    
    path('grades/', views.grade_list, name='grade_list'),
    path('grades/create/', views.grade_create, name='grade_create'),
    path('grades/update/<int:id>/', views.grade_update, name='grade_update'),
    path('grades/delete/<int:id>/', views.grade_delete, name='grade_delete'),

    path('uploadstud/', views.upload_student_csv, name='upload_students'),

]
