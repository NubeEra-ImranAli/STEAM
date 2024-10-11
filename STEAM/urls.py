from django.urls import path,include
from django.contrib import admin
from steamapp import views
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from steamapp import activate

urlpatterns = [
    path('students/', views.student_list, name='student_list'),
    path('insert-students/', views.insert_students, name='insert_students'),
    path('admin/', admin.site.urls),
    path('check-username/', views.check_username, name='check_username'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('switch-user', views.switch_user_view,name='switch-user'),
    path('reset-user/<int:pk>', views.reset_user_view,name='reset-user'),

    path("", views.home, name='home'),
    path('student/',include('student.urls')), 
    
    path('indexpage/', views.afterlogin_view,name='indexpage'),   
    path('user-session-expired', views.session_expire_view,name='user-session-expired'),   

    path('adminclick', views.adminclick_view),
    path('userlogin', LoginView.as_view(template_name='loginrelated/userlogin.html'),name='userlogin'),
    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),
    path('admin-view-user-log-details/<int:user_id>', views.admin_view_user_log_details_view,name='admin-view-user-log-details'),
    path('admin-view-user-activity-details/<int:user_id>', views.admin_view_user_activity_details_view,name='admin-view-user-activity-details'),
    path('admin-view-user-list', views.admin_view_user_list_view,name='admin-view-user-list'),
    path('update-user/<int:pk>', views.update_user_view,name='update-user'),
    path('active-user/<int:pk>', views.active_user_view,name='active-user'),
    path('delete-user/<userid>/<int:pk>', views.delete_user_view,name='delete-user'),
    
    path('activate/<str:uidb64>/<str:token>/', activate.activate, name='activate'),
    
    path('userlogin/', views.user_login,name='userlogin'),
    path('register', LoginView.as_view(template_name='loginrelated/register.html'),name='register'),
    path('user-change-password', views.user_change_password_view,name='user-change-password'),
]
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
    