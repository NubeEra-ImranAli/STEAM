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
        self.stdout.write(self.style.SUCCESS('Schools created successfully...'))
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
        self.stdout.write(self.style.SUCCESS('Grades created successfully...'))

        
        self.stdout.write(self.style.NOTICE('Creating Divisions...'))
                
        MyModels.Division.objects.create(
                division_name = 'A',
            ).save()
        
        MyModels.Division.objects.create(
                division_name = 'B',
            ).save()
        
        MyModels.Division.objects.create(
                division_name = 'C',
            ).save()
        
        MyModels.Division.objects.create(
                division_name = 'D',
            ).save()
        
        MyModels.Division.objects.create(
                division_name = 'E',
            ).save()
        MyModels.Division.objects.create(
                division_name = 'F',
            ).save()
        MyModels.Division.objects.create(
                division_name = 'G',
            ).save()
        MyModels.Division.objects.create(
                division_name = 'H',
            ).save()
        MyModels.Division.objects.create(
                division_name = 'I',
            ).save()

        self.stdout.write(self.style.SUCCESS('Divisions created successfully...'))