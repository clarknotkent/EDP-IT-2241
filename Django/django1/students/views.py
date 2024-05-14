from django.shortcuts import render, redirect, get_object_or_404
from students.models import StudentRecord
from students.forms import StudentRecordForm
from django.db.models import Q

def students(request):
    context = {}
    form = StudentRecordForm()
    table = StudentRecord.objects.all()
    
    search = request.GET.get('search', '')
    filterCourses = request.GET.getlist('filterCourses')
    filterGender = request.GET.get('filterGender', 'all')
    minAge = request.GET.get('minAge')
    maxAge = request.GET.get('maxAge')
    
    # Filtering logic
    if search:
        table = table.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search))
    if filterCourses:
        table = table.filter(course__in=filterCourses)
    if filterGender != 'all':
        table = table.filter(gender=filterGender)
    if minAge:
        table = table.filter(age__gte=minAge)
    if maxAge:
        table = table.filter(age__lte=maxAge)
    
    context['table'] = table
    context['title'] = 'Students Table'
    context['courses'] = [choice[0] for choice in StudentRecord.COURSE_CHOICES]
    
    if request.method == 'POST':
        if 'delete' in request.POST:
            pk = request.POST.get('delete')
            stud = StudentRecord.objects.get(id=pk)
            stud.delete()
            return redirect('students.index')
    
    context['form'] = form
    return render(request, 'students.html', context)

def add(request):
    context = {}
    form = StudentRecordForm()
    data = StudentRecord.objects.all()
    context['data'] = data
    context['title'] = 'Add Form'
    if request.method == 'POST':
        form = StudentRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('students.index')
    context['form'] = form    
    return render(request, 'add.html', context)

def update(request, pk):
    student = get_object_or_404(StudentRecord, pk=pk)
    if request.method == 'POST':
        form = StudentRecordForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('students.index')
    else:
        form = StudentRecordForm(instance=student)
    
    context = {
        'form': form,
        'title': 'Update Student',
        'student': student,
    }
    return render(request, 'update.html', context)
