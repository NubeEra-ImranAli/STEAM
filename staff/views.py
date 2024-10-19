import os
from steamapp import models as MyModels
from django.contrib import messages
from django.core.files.storage import default_storage
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

ROMAN_NUMERAL_MAP = {
                        'V': 5,
                        'VI': 6,
                        'VII': 7,
                        'VIII': 8,
                        'IX': 9,
                        'X': 10,
                    }


# Display list of schools
@login_required
def school_list(request):
    if str(request.session['utype']) == 'staff':
        schools = MyModels.School.objects.all()
        return render(request, 'staff/school/school_list.html', {'schools': schools})
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Create a new school
@login_required
def school_create(request):
    if str(request.session['utype']) == 'staff':
        if request.method == 'POST':
            school_name = request.POST.get('school_name')
            contact_person = request.POST.get('contact_person')
            email = request.POST.get('email')
            address = request.POST.get('address')
            phone_number = request.POST.get('phone_number')

            if school_name:
                MyModels.School.objects.create(
                                                school_name=school_name,
                                                contact_person=contact_person,
                                                email=email,
                                                address=address,
                                                phone_number=phone_number
                                                )
                messages.success(request, 'School created successfully!')
                return redirect('school_create')
        return render(request, 'staff/school/school_create.html')
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Update an existing school
@login_required
def school_update(request, id):
    if str(request.session['utype']) == 'staff':
        school = get_object_or_404(MyModels.School, id=id)
        if request.method == 'POST':
            school_name = request.POST.get('school_name')
            contact_person = request.POST.get('contact_person')
            email = request.POST.get('email')
            address = request.POST.get('address')
            phone_number = request.POST.get('phone_number')
            if school_name:
                school.school_name = school_name
                school.contact_person = contact_person
                school.email = email
                school.address = address
                school.phone_number = phone_number
                school.save()
                return redirect('school_list')
        return render(request, 'staff/school/school_update.html', {'school': school})
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Delete a school
@login_required
def school_delete(request, id):
    if str(request.session['utype']) == 'staff':
        school = get_object_or_404(MyModels.School, id=id)
        school.delete()
        return redirect('school_list')
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Display list of grades
@login_required
def grade_list(request):
    if str(request.session['utype']) == 'staff':
        grades = MyModels.Grade.objects.all()
        return render(request, 'staff/grade/grade_list.html', {'grades': grades})
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Create a new grade
@login_required
def grade_create(request):
    if str(request.session['utype']) == 'staff':
        if request.method == 'POST':
            grade_name = request.POST.get('grade_name')
            if grade_name:
                MyModels.Grade.objects.create(grade_name=grade_name)
                messages.success(request, 'Grade created successfully!')
                return redirect('grade_create')
        return render(request, 'staff/grade/grade_create.html')
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Update an existing grade
@login_required
    
def grade_update(request, id):
    if str(request.session['utype']) == 'staff':
        grade = get_object_or_404(MyModels.Grade, id=id)
        if request.method == 'POST':
            grade_name = request.POST.get('grade_name')
            if grade_name:
                grade.grade_name = grade_name
                grade.save()
                return redirect('grade_list')
        return render(request, 'staff/grade/grade_update.html', {'grade': grade})
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Delete a grade
@login_required
def grade_delete(request, id):
    if str(request.session['utype']) == 'staff':
        grade = get_object_or_404(MyModels.Grade, id=id)
        grade.delete()
        return redirect('grade_list')
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Display list of divisions
@login_required
def division_list(request):
    if str(request.session['utype']) == 'staff':
        divisions = MyModels.Division.objects.all()
        return render(request, 'staff/division/division_list.html', {'divisions': divisions})
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Create a new division
@login_required
def division_create(request):
    if str(request.session['utype']) == 'staff':
        if request.method == 'POST':
            division_name = request.POST.get('division_name')
            if division_name:
                MyModels.Division.objects.create(division_name=division_name)
                messages.success(request, 'Division created successfully!')
                return redirect('division_create')
        return render(request, 'staff/division/division_create.html')
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Update an existing division
@login_required
    
def division_update(request, id):
    if str(request.session['utype']) == 'staff':
        division = get_object_or_404(MyModels.Division, id=id)
        if request.method == 'POST':
            division_name = request.POST.get('division_name')
            if division_name:
                division.division_name = division_name
                division.save()
                return redirect('division_list')
        return render(request, 'staff/division/division_update.html', {'division': division})
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Delete a division
@login_required
def division_delete(request, id):
    if str(request.session['utype']) == 'staff':
        division = get_object_or_404(MyModels.Division, id=id)
        division.delete()
        return redirect('division_list')
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Display list of modules
@login_required
def module_list(request):
    if str(request.session['utype']) == 'staff':
        modules = MyModels.Module.objects.all()
        return render(request, 'staff/module/module_list.html', {'modules': modules})
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Create a new module
@login_required
def module_create(request):
    if str(request.session['utype']) == 'staff':
        if request.method == 'POST':
            grade = request.POST.get('grade')
            module_name = request.POST['module_name']
            description = request.POST['description']
            module_pic = request.FILES.get('module_pic')  # Fetch the file if uploaded
            if module_name:
                mode = MyModels.Module.objects.create(grade_id=grade,module_name=module_name,description=description)

                if module_pic:
                    # Generate the custom file name: username_userid.extension
                    file_extension = os.path.splitext(module_pic.name)[1]  # Get the file extension
                    new_file_name = f"{mode.module_name}_{mode.id}_{grade}{file_extension}"
                    
                    # Define the path where the file will be saved
                    file_path = mode.module_pic.storage.path(new_file_name)
                    
                    # Check if a file with the same name exists and delete it
                    if default_storage.exists(new_file_name):
                        default_storage.delete(new_file_name)

                    # Save the new profile pic with the new file name
                    mode.module_pic.save(new_file_name, module_pic)
                mode.save()
                messages.success(request, 'Module created successfully!')
                return redirect('module_create')
        grade = MyModels.Grade.objects.filter(id__isnull=False)\
                        .values('id','grade_name')
        grade = sorted(
                            grade,
                            key=lambda x: (ROMAN_NUMERAL_MAP.get(x['grade_name'], 0))
                        )
        return render(request, 'staff/module/module_create.html',{'grades':grade})
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Update an existing module
@login_required
    
def module_update(request, id):
    if str(request.session['utype']) == 'staff':
        if request.method == 'POST':
            grade = request.POST.get('grade')
            module_name = request.POST['module_name']
            description = request.POST['description']
            module_pic = request.FILES.get('module_pic')  # Fetch the file if uploaded

            
            mode = get_object_or_404(MyModels.Module, id=id)
            mode.grade_id = grade
            mode.module_name = module_name
            mode.description = description
            
            if module_pic:
                # Generate the custom file name: username_userid.extension
                file_extension = os.path.splitext(module_pic.name)[1]  # Get the file extension
                new_file_name = f"{mode.module_name}_{mode.id}_{grade}{file_extension}"
                
                # Define the path where the file will be saved
                file_path = mode.module_pic.storage.path(new_file_name)
                
                # Check if a file with the same name exists and delete it
                if default_storage.exists(new_file_name):
                    default_storage.delete(new_file_name)

                # Save the new profile pic with the new file name
                mode.module_pic.save(new_file_name, module_pic)
            mode.save()
            messages.success(request, 'Module updated successfully!' if id else 'Module created successfully!')
            return redirect('module_list')

        # Load the module details if updating
        module = None
        module = get_object_or_404(MyModels.Module, id=id)

        grades = MyModels.Grade.objects.filter(id__isnull=False).values('id', 'grade_name')
        grades = sorted(grades, key=lambda x: (ROMAN_NUMERAL_MAP.get(x['grade_name'], 0)))

        return render(request, 'staff/module/module_update.html', {
            'grades': grades,
            'module': module,
        })
    else:
        return render(request, 'loginrelated/diffrentuser.html')

# Delete a module
@login_required
def module_delete(request, id):
    if str(request.session['utype']) == 'staff':
        module = get_object_or_404(MyModels.Module, id=id)
        
        # Check if there is a module_pic and delete the file if it exists
        if module.module_pic:
            # Construct the full file path
            file_path = os.path.join(settings.MEDIA_ROOT, str(module.module_pic))
            
            # Delete the file if it exists
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # Now delete the module instance
        module.delete()
        
        return redirect('module_list')
    else:
        return render(request,'loginrelated/diffrentuser.html')
    
def get_modules(request):
    grade_id = request.GET.get('grade_id')
    modules = MyModels.Module.objects.filter(grade_id=grade_id).values('id', 'module_name')
    return JsonResponse(list(modules), safe=False)

    # Display list of lessons
@login_required
def lesson_list(request):
    if str(request.session['utype']) == 'staff':
        lessons = MyModels.Lesson.objects.all()
        return render(request, 'staff/lesson/lesson_list.html', {'lessons': lessons})
    else:
        return render(request,'loginrelated/diffrentuser.html')

@login_required
    
def lesson_preview(request, id):
    if str(request.session['utype']) == 'staff':
        les = get_object_or_404(MyModels.Lesson, id=id)
        grade = les.grade_id
        module = les.module_id
        heading = les.heading
        about =  les.about 
        reqmaterial = les.reqmaterial 
        digram = les.digram
        code = les.code
        process = les.process
        get = les.get
        video = les.video
        return render(request, 'staff/lesson/lesson_preview.html', {
            'grade': grade,
            'module': module,
            'heading': heading,
            'about': about,
            'reqmaterial': reqmaterial,
            'digram': digram,
            'code': code,
            'process': process,
            'get': get,
            'video': video,
        })
    else:
        return render(request, 'loginrelated/diffrentuser.html')

# Create a new lesson
@login_required
def lesson_create(request):
    if str(request.session['utype']) == 'staff':
        if request.method == 'POST':
            grade = request.POST.get('grade')
            module = request.POST.get('module')
            serialno = request.POST['serialno']
            heading = request.POST['heading']
            about = request.POST['about']
            reqmaterial = request.POST['reqmaterial']
            digram = request.POST['digram']
            code = request.POST['code']
            process = request.POST['process']
            get = request.POST['get']
            video = request.POST['video']
            mode = MyModels.Lesson.objects.create(grade_id=grade,
                                                  module_id=module,
                                                  serialno = serialno,
                                                  heading=heading,
                                                  about=about,
                                                  reqmaterial=reqmaterial,
                                                  digram=digram,
                                                  code=code,
                                                  process=process,
                                                  get=get,
                                                  video=video
                                                  )
            mode.save()
            messages.success(request, 'Lesson created successfully!')
            return redirect('lesson_create')
        grade = MyModels.Grade.objects.filter(id__isnull=False)\
                        .values('id','grade_name')
        grade = sorted(
                            grade,
                            key=lambda x: (ROMAN_NUMERAL_MAP.get(x['grade_name'], 0))
                        )
        
        return render(request, 'staff/lesson/lesson_create.html',{'grades':grade})
    else:
        return render(request,'loginrelated/diffrentuser.html')

# Update an existing lesson
@login_required
    
def lesson_update(request, id):
    if str(request.session['utype']) == 'staff':
        if request.method == 'POST':
            grade = request.POST.get('grade')
            module = request.POST.get('module')
            serialno = request.POST['serialno']
            heading = request.POST['heading']
            about = request.POST['about']
            reqmaterial = request.POST['reqmaterial']
            digram = request.POST['digram']
            code = request.POST['code']
            process = request.POST['process']
            get = request.POST['get']
            video = request.POST['video']
            
            les = get_object_or_404(MyModels.Lesson, id=id)
            les.grade_id = grade
            les.module = module
            les.serialno = serialno
            les.heading = heading
            les.about = about
            les.reqmaterial = reqmaterial
            les.digram = digram
            les.code = code
            les.process = process
            les.get = get
            les.video = video
            les.save()
            messages.success(request, 'Lesson updated successfully!' if id else 'Lesson created successfully!')
            return redirect('lesson_list')

        grades = MyModels.Grade.objects.filter(id__isnull=False).values('id', 'grade_name')
        grades = sorted(grades, key=lambda x: (ROMAN_NUMERAL_MAP.get(x['grade_name'], 0)))

        les = get_object_or_404(MyModels.Lesson, id=id)
        grade = les.grade_id
        module = les.module_id
        serialno = les.serialno
        heading = les.heading
        about =  les.about 
        reqmaterial = les.reqmaterial 
        digram = les.digram
        code = les.code
        process = les.process
        get = les.get
        video = les.video
        return render(request, 'staff/lesson/lesson_update.html', {
            'grades': grades,
            'grade': grade,
            'module': module,
            'serialno' :serialno,
            'heading': heading,
            'about': about,
            'reqmaterial': reqmaterial,
            'digram': digram,
            'code': code,
            'process': process,
            'get': get,
            'video': video,
        })
    else:
        return render(request, 'loginrelated/diffrentuser.html')

# Delete a lesson
@login_required
def lesson_delete(request, id):
    if str(request.session['utype']) == 'staff':
        lesson = get_object_or_404(MyModels.Lesson, id=id)
        
        # Check if there is a lesson_pic and delete the file if it exists
        if lesson.lesson_pic:
            # Construct the full file path
            file_path = os.path.join(settings.MEDIA_ROOT, str(lesson.lesson_pic))
            
            # Delete the file if it exists
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # Now delete the lesson instance
        lesson.delete()
        
        return redirect('lesson_list')
    else:
        return render(request,'loginrelated/diffrentuser.html')

import uuid
from urllib.parse import urljoin
import requests
from django.http import JsonResponse
import base64  # Import the base64 module
# Load the Git access token from environment variables

GIT_REPO_URL = "https://oauth:NubeEra-ImranAli@github.com/NubeEra-ImranAli/study_kit.git"
GITHUB_RAW_BASE_URL = "https://raw.githubusercontent.com/NubeEra-ImranAli/study_kit/main/"
GIT_API_URL = "https://api.github.com/repos/NubeEra-ImranAli/study_kit/contents/"

def load_file_mapping():
    headers = {
        "Authorization": f"Bearer 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"  # Use your GitHub personal access token
    }
    response = requests.get(GIT_API_URL, headers=headers)

    if response.status_code == 200:
        return {file['name']: str(uuid.uuid4()) for file in response.json()}
            
    else:
        return {}
def upload_html_file(request):
    if request.method == "POST":
        # Get the uploaded file
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name

        # Prepare the API URL and headers
        api_url = f"{GIT_API_URL}{file_name}"
        headers = {
            "Authorization": f"Bearer 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",  # Use your GitHub personal access token
            "Content-Type": "application/json"
        }

        # Read the content of the uploaded file
        content = uploaded_file.read().decode('utf-8')
        # Prepare data to send to GitHub
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        data = {
            "message": f"Add {file_name}",
            "content": encoded_content,
            "branch": "main"
        }

        # Send the PUT request to GitHub
        response = requests.put(api_url, headers=headers, json=data)

        if response.status_code == 201:
            return redirect('view_html')  # Redirect to the file list view
        else:
            return JsonResponse({"error": "Failed to upload file"}, status=response.status_code)

    return render(request, 'steamapp/upload.html')

def view_html_file(request):
    file_mapping = load_file_mapping()  # Load file mapping each time
    return render(request, 'steamapp/file_list.html', {
        'file_mapping': file_mapping
    })