from django.contrib import admin
from students.models import StudentRecord

class StudentRecordAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','course','gender','age']

# Register your models here.
admin.site.register(StudentRecord, StudentRecordAdmin)