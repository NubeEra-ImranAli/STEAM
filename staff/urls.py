from django.urls import path
from staff import views

urlpatterns = [

    path('schools/', views.school_list, name='school_list'),
    path('schools/create/', views.school_create, name='school_create'),
    path('schools/update/<int:id>/', views.school_update, name='school_update'),
    path('schools/delete/<int:id>/', views.school_delete, name='school_delete'),

    path('grades/', views.grade_list, name='grade_list'),
    path('grades/create/', views.grade_create, name='grade_create'),
    path('grades/update/<int:id>/', views.grade_update, name='grade_update'),
    path('grades/delete/<int:id>/', views.grade_delete, name='grade_delete'),

    path('divisions/', views.division_list, name='division_list'),
    path('divisions/create/', views.division_create, name='division_create'),
    path('divisions/update/<int:id>/', views.division_update, name='division_update'),
    path('divisions/delete/<int:id>/', views.division_delete, name='division_delete'),
    
    path('modules/', views.module_list, name='module_list'),
    path('modules/create/', views.module_create, name='module_create'),
    path('modules/update/<int:id>/', views.module_update, name='module_update'),
    path('modules/delete/<int:id>/', views.module_delete, name='module_delete'),
]
