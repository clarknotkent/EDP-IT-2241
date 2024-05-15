from django.db import models

# Create your models here.
class StudentRecord(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    COURSE_CHOICES = [
        ('BS-IT', 'BS-IT'),
        ('BS-CS', 'BS-CS'),
        ('BS-DS', 'BS-DS'),
        ('BS-IS', 'BS-IS'),
        # Add more choices as needed
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    course = models.CharField(max_length=50, choices=COURSE_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.course} {self.gender} {self.age}"
    
    # class Meta:
    #     ordering = ['last_name']