from django.core.management.base import BaseCommand
from steamapp import models as MyModels
class Command(BaseCommand):
    help = 'Create a Demo schools and grades'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Creating Schools...'))
        for i in range (26):
            MyModels.School.objects.create(
                school_name = f'School {i}',
                contact_person = f'Sir {i}',
                email = 'email@mailservice.com',
                address = 'School address',
                phone_number = '1234567890'
            ).save()
        self.stdout.write(self.style.NOTICE('Schools created successfully...'))
        self.stdout.write(self.style.NOTICE('Creating Grades...'))
        
        MyModels.Grade.objects.create(
                grade_name = 'V',
            ).save()
        
        MyModels.Grade.objects.create(
                grade_name = 'VI',
            ).save()
        
        MyModels.Grade.objects.create(
                grade_name = 'VII',
            ).save()
        
        MyModels.Grade.objects.create(
                grade_name = 'VIII',
            ).save()
        
        MyModels.Grade.objects.create(
                grade_name = 'IX',
            ).save()
        
        
