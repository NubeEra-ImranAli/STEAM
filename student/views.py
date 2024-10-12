from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from steamapp import models as LXPModel
from steamapp import forms as LXPFORM
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum,Count,Q
from django.urls import reverse
@login_required    
def student_dashboard_view(request):
    #try:
        if str(request.session['utype']) == 'student':
            dict={
            'total_course':0,
            'total_exam':0,
            'total_shortExam':0, 
            'total_question':0,
            'total_short':0,
            'total_learner':0,
            }
            return render(request,'student/student_dashboard.html',context=dict)
        else:
            return render(request,'loginrelated/diffrentuser.html')
    #except:
        return render(request,'loginrelated/diffrentuser.html')
 
