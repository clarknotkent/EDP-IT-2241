from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class StudentRecord(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    COURSE_CHOICES = [
        ('BS-IT', 'BS Information Technology'),
        ('BS-CS', 'BS Computer Science'),
        ('BS-DS', 'BS Data Science'),
        ('BS-IS', 'BS Information Systems'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    course = models.CharField(max_length=50, choices=COURSE_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.PositiveSmallIntegerField(
        # PositiveSmallIntegerField alone accepts 0-32767; the admin log in the
        # submitted database has a student aged 444.
        validators=[MinValueValidator(1), MaxValueValidator(120)],
    )

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'

    def get_absolute_url(self):
        return reverse('students:detail', args=[self.pk])

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
