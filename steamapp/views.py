
import os
from django.shortcuts import render,redirect
from steamapp import forms,models
from django.http import HttpResponseRedirect
from django.conf import settings
from steamapp.models import User
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from datetime import datetime
login_time = datetime.now()
logout_time  = datetime.now()
from django.http import HttpResponse
from django.contrib.auth import logout
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as userlogin
from django.http import HttpResponse
from django.db import IntegrityError
from django.core.files.storage import default_storage
def logout_view(request):
    logout(request)
    return redirect('userlogin')

@login_required
def switch_user_view(request):
    logout(request)
    return redirect('userlogin')

def check_username(request):
    if request.method == "GET":
        username = request.GET.get('username', None)
        is_taken = User.objects.filter(username=username).exists()
        return JsonResponse({'is_taken': is_taken})

def signup(request):
    if request.method == "POST":
        # Get form data
        first_name = request.POST['first_name'].strip()
        last_name = request.POST['last_name'].strip()
        username = request.POST['username'].strip()
        password = request.POST['password']
        profile_pic = request.FILES.get('profile_pic')  # Fetch the file if uploaded
        banner_pics = request.FILES.get('banner_pic')  # Fetch the file if uploaded
        mobile = request.POST['mobile'].strip()
        whatsappno = request.POST['whatsappno'].strip()
        
        # Create user
        try:
            newuser = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                mobile=mobile,
                whatsappno=whatsappno,
                username=username,
                password=password
            )

            # If a profile picture was uploaded
            if profile_pic:
                # Generate the custom file name: username_userid.extension
                file_extension = os.path.splitext(profile_pic.name)[1]  # Get the file extension
                new_file_name = f"{username}_{newuser.id}{file_extension}"

                # Save the profile pic with the new file name
                newuser.profile_pic.save(new_file_name, profile_pic)

            # If a banner picture was uploaded
            if banner_pics:
                # Generate the custom file name: username_userid.extension
                file_extension = os.path.splitext(banner_pics.name)[1]  # Get the file extension
                new_file_name = f"{username}_{newuser.id}{file_extension}"

                # Save the profile pic with the new file name
                newuser.banner_pic.save(new_file_name, banner_pics)

            # Save the user instance (if banner_pics is updated)
            newuser.save()

            users = User.objects.all().filter(is_superuser = False)
            return HttpResponseRedirect('/admin-view-user-list',{'users':users})
            
        except IntegrityError:
            return HttpResponse("A user with that username already exists.")
        except Exception as e:
            return HttpResponse(f"Something went wrong: {e}")

    return render(request, 'loginrelated/signup.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            userlogin(request, user)
            return redirect('home')  # Redirect to a success page.
        else:
            return render(request, 'loginrelated/userlogin.html', {'error_message': 'Invalid username or password.'})
    else:
        return render(request, 'loginrelated/userlogin.html')
def session_expire_view(request):
    A = models.LastUserLogin.objects.all()
    if A:
        for x in A:
            id = x.id
            logout_time = datetime.now()
            dur = str( logout_time - login_time).split(".")[0]
            userlog = models.UserLog.objects.create(
                    user_id = id,
                    login = login_time,
                    logout = logout_time,
                    dur = dur
                    )
            userlog.save()
    models.LastUserLogin.objects.all().delete()
    return render(request, 'loginrelated/user_session_expire.html')

@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    if not user.is_staff:
        pic = "UserSocialAuth.objects.only('pic').get(user_id=user.id).pic"
    login_time = datetime.now()

@receiver(user_logged_out)
def post_logout(sender, user, request, **kwargs):
    logout_time = datetime.now()
    dur = str( logout_time - login_time).split(".")[0]
    userlog = models.UserLog.objects.create(
              user = user,
              login = login_time,
              logout = logout_time,
              dur = dur
            )
    userlog.save()
    models.LastUserLogin.objects.all().delete()

@login_required
def user_change_password_view(request):
    try:    
        sub = forms.ContactusForm()
        if request.method == 'POST':
            u = request.user
            u.set_password(request.POST['passid'])
            u.save() # Add this line
            update_session_auth_hash(request, u)
            return HttpResponseRedirect('indexpage')  
        return render(request, 'loginrelated/changepassword.html')
    except:
        return render(request,'loginrelated/diffrentuser.html')

def home(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('indexpage'))
    else:
        return HttpResponseRedirect(reverse('userlogin'))

    return render(request,'loginrelated/diffrentuser.html')


def afterlogin_view(request):
    user = User.objects.all().filter(id = request.user.id)

    if user:
        for xx in user:
            if xx.is_superuser:
                request.session['utype'] = 'admin'
                return redirect('admin-dashboard')
            if xx.utype == 'CANDIDATE':
                if xx.status:
                    request.session['utype'] = 'CANDIDATE'
                    dict={
                    'total_course':0,
                    'total_exam':0,
                    'total_shortExam':0, 
                    'total_question':0,
                    'total_short':0,
                    'total_learner':0,
                    }
                    return render(request,'student/candidate_dashboard.html',context=dict)
                else:
                    return render(request,'loginrelated/wait_for_approval.html')
    else:
        return render(request, 'loginrelated/userlogin.html')

def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('indexpage')
    return HttpResponseRedirect('userlogin')

@login_required
def admin_dashboard_view(request):
    #try:
        if str(request.session['utype']) == 'admin':
            dict={
            'total_learner':0,
            'total_candidate':0,
            'total_exam':0,
            'total_question':0,
            }
            return render(request,'steamapp/admin_dashboard.html',context=dict)
    #except:
        return render(request,'loginrelated/diffrentuser.html')

@login_required
def admin_view_user_list_view(request):
    #try:    
        if str(request.session['utype']) == 'admin':
            users = User.objects.all().filter(is_superuser = False)
            for x in users:
                print(x)
            return render(request,'steamapp/users/admin_view_user_list.html',{'users':users})
    #except:
        return render(request,'loginrelated/diffrentuser.html')

    
def admin_view_user_log_details_view(request,user_id):
    try:    
        if str(request.session['utype']) == 'admin':
            users = models.UserLog.objects.all().filter(user_id = user_id)
            return render(request,'steamapp/users/admin_view_user_log_details.html',{'users':users})
    except:
        return render(request,'loginrelated/diffrentuser.html')

@login_required
def admin_view_user_activity_details_view(request,user_id):
    #try:    
        if str(request.session['utype']) == 'admin':
            users = models.UserActivity.objects.all().filter(user_id = user_id)
            return render(request,'steamapp/users/admin_view_user_activity_details.html',{'users':users})
    #except:
        return render(request,'loginrelated/diffrentuser.html')

@login_required
def update_user_view(request, pk):
    if str(request.session['utype']) == 'admin':
        if request.method == 'POST':
            first_name = request.POST['first_name'].strip()
            last_name = request.POST['last_name'].strip()
            profile_pic = request.FILES.get('profile_pic')  # Fetch the file if uploaded
            banner_pic = request.FILES.get('banner_pic')  # Fetch the file if uploaded
            mobile = request.POST['mobile'].strip()
            whatsappno = request.POST['whatsappno'].strip()

            user = User.objects.get(id=pk)
            user.first_name = first_name
            user.last_name = last_name
            user.mobile = mobile
            user.whatsappno = whatsappno

            # Handle profile picture update
            if profile_pic:
                # Delete the old profile picture if it exists
                if user.profile_pic:
                    if default_storage.exists(user.profile_pic.name):
                        default_storage.delete(user.profile_pic.name)
                # Generate the custom file name: username_userid.extension
                file_extension = os.path.splitext(profile_pic.name)[1]  # Get the file extension
                new_file_name = f"{user.username}_{pk}{file_extension}"

                # Save the new profile picture
                user.profile_pic.save(new_file_name, profile_pic)

            # Handle banner picture update
            if banner_pic:
                # Delete the old banner picture if it exists
                if user.banner_pic:
                    if default_storage.exists(user.banner_pic.name):
                        default_storage.delete(user.banner_pic.name)
                # Generate the custom file name: username_userid.extension
                file_extension = os.path.splitext(banner_pic.name)[1]  # Get the file extension
                new_file_name = f"{user.username}_{pk}{file_extension}"

                # Save the new banner picture
                user.banner_pic.save(new_file_name, banner_pic)

            user.save()
            
            users = User.objects.filter(is_superuser=False)
            return HttpResponseRedirect('/admin-view-user-list', {'user': users})
        
        users = User.objects.get(id=pk)
        return render(request, 'steamapp/users/admin_update_user.html', {'users': users})

    return render(request,'loginrelated/diffrentuser.html')
@login_required
def active_user_view(request, pk):
    if str(request.session['utype']) == 'admin':
        try:
            user = User.objects.get(id=pk)
            user.status = not user.status  # Toggle status
            user.save()
            return JsonResponse({'success': True, 'status': user.status})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
    return JsonResponse({'success': False, 'error': 'Unauthorized'})

@login_required
def reset_user_view(request, pk):
    if str(request.session['utype']) == 'admin':
        try:
            user = User.objects.get(id=pk)
            user.set_password('steamapp@123')
            user.save()
            update_session_auth_hash(request, user)
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
    return JsonResponse({'success': False, 'error': 'Unauthorized'})
@login_required
def delete_user_view(request,pk):
    try:    
        if str(request.session['utype']) == 'admin':
            users = models.User.objects.get(id = pk)
            users.delete()
            users = User.objects.all().filter(is_superuser = False)
            return HttpResponseRedirect('/admin-view-user-list',{'users':users})
    except:
        return render(request,'loginrelated/diffrentuser.html')
    
import string
from .models import Student
import random
from datetime import datetime, timedelta
def random_string(length=10):
    """Generate a random string of fixed length."""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def random_email():
    """Generate a random email address."""
    return f"{random_string(10)}@example.com"

def random_date_of_birth():
    """Generate a random date of birth."""
    start_date = datetime(1950, 1, 1)
    end_date = datetime(2005, 12, 31)
    delta = end_date - start_date
    random_days = random.randrange(delta.days)
    return start_date + timedelta(days=random_days)

def insert_students(request):
    num_records = 100  # Adjust this as needed for testing
    
    for _ in range(num_records):
        Student.objects.create(
            first_name=random_string(8),
            last_name=random_string(8),
            email=random_email(),
            date_of_birth=random_date_of_birth(),
            address=f'{random.randint(1, 9999)} {random_string(5)} St',
            phone_number=f'(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}',
            gender=random.choice(['Male', 'Female']),
            enrollment_date=datetime.now() - timedelta(days=random.randint(1, 3650)),
            
        )
    
    return HttpResponse(f"{num_records} records inserted!")

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
def student_list(request):
    form = forms.StudentSearchForm(request.GET or None)
    students = Student.objects.all()
    
    if form.is_valid():
        cleaned_data = form.cleaned_data
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        gender = cleaned_data.get('gender')
        address = cleaned_data.get('address')
        
        if first_name:
            students = students.filter(first_name__icontains=first_name)
        if last_name:
            students = students.filter(last_name__icontains=last_name)
        if email:
            students = students.filter(email__icontains=email)
        if gender:
            students = students.filter(gender=gender)
        if address:
            students = students.filter(address__icontains=address)

    # Handle results per page
    results_per_page = request.GET.get('results_per_page', 10)  # Default to 10 if not specified
    paginator = Paginator(students, results_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Return data as JSON
        students_data = list(page_obj.object_list.values('first_name', 'last_name', 'email', 'gender', 'address'))
        return JsonResponse({
            'students': students_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'current_page': page_obj.number,
            'total_pages': page_obj.paginator.num_pages
        })
    
    return render(request, 'student_list.html', {'form': form, 'page_obj': page_obj})