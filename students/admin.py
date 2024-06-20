from django.contrib import admin

from students.models import StudentRecord


@admin.register(StudentRecord)
class StudentRecordAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'course', 'gender', 'age']
    list_filter = ['course', 'gender']
    search_fields = ['first_name', 'last_name']
    ordering = ['last_name', 'first_name']
