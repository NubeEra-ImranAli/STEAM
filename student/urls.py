from django.urls import path
from student import views
from django.contrib.auth.views import LoginView

urlpatterns = [

    path('student-dashboard', views.student_dashboard_view,name='student-dashboard'),
    
]
