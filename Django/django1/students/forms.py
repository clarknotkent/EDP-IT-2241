from django import forms
from students.models import StudentRecord

class StudentRecordForm(forms.ModelForm):
    class Meta:
        model = StudentRecord
        fields = ['first_name', 'last_name', 'course', 'gender', 'age']
        widgets = {
            'gender': forms.RadioSelect(choices=StudentRecord.GENDER_CHOICES),
        }
