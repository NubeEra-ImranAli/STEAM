from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from . import models

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
                'username', 
                'password',
                'first_name', 
                'last_name'
        ]

class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))

class LearnerDetailsForm(forms.ModelForm):
    user_full_name = forms.CharField(
        max_length=90000,
        #  forms ↓
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    class Meta:
        fields=['user_full_name','mobile','iswhatsapp','whatsappno']


class StudentSearchForm(forms.Form):
    first_name = forms.CharField(required=False, label='First Name')
    last_name = forms.CharField(required=False, label='Last Name')
    email = forms.EmailField(required=False, label='Email')
    gender = forms.ChoiceField(required=False, choices=[('', 'All'), ('Male', 'Male'), ('Female', 'Female')], label='Gender')
    address = forms.CharField(required=False, label='Address')