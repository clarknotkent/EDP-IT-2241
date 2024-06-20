import csv

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from students.forms import StudentRecordForm
from students.models import StudentRecord
from students.selectors import (
    SORT_FIELDS,
    filtered_students,
    is_filtered,
    read_filters,
)


def _sort_links(filters, querystring):
    """One entry per sortable column: where it points and how it reads.

    A header that sorts must say which way it sorts, and say it to a screen
    reader too - hence aria-sort, not just an arrow.
    """
    links = {}
    for key in SORT_FIELDS:
        active = filters['sort'] == key
        # Clicking the active column flips it; clicking another starts ascending.
        next_dir = 'desc' if active and filters['dir'] == 'asc' else 'asc'
        params = querystring.copy()
        params['sort'] = key
        params['dir'] = next_dir
        params.pop('page', None)
        links[key] = {
            'url': '?' + params.urlencode(),
            'active': active,
            'dir': filters['dir'] if active else '',
            'aria': (
                {'asc': 'ascending', 'desc': 'descending'}[filters['dir']]
                if active else 'none'
            ),
        }
    return links


@login_required
def student_list(request):
    filters = read_filters(request.GET)
    students = filtered_students(filters)

    # The list view rendered every row. Fine for the four records in the
    # submitted database, not for a table that is meant to grow.
    paginator = Paginator(students, settings.PAGE_SIZE)
    page = paginator.get_page(request.GET.get('page'))

    # Filters have to survive page and sort links, so build the query string
    # once without `page` rather than re-adding each parameter in the template.
    querystring = request.GET.copy()
    querystring.pop('page', None)

    return render(request, 'students_list.html', {
        'title': 'Students',
        'page': page,
        'students': page.object_list,
        # `total` is how many matched; `total_all` is how many exist. The
        # empty state and the "N matching / M total" line need both, and
        # conflating them reports "0 records exist" on a filtered miss.
        'total': paginator.count,
        'total_all': StudentRecord.objects.count(),
        'querystring': querystring.urlencode(),
        'course_choices': StudentRecord.COURSE_CHOICES,
        'gender_choices': [('all', 'All'), *StudentRecord.GENDER_CHOICES],
        'sort_links': _sort_links(filters, querystring),
        'is_filtered': is_filtered(filters),
        # The template needs the *list* of selected courses. Reading
        # request.GET.course in the template yields only the last value, and
        # `in` on a string does substring matching - which is how the original
        # lost every checkbox but one on each request.
        'filters': filters,
    })


@login_required
def student_export(request):
    """CSV of everything currently filtered - not just the page on screen.

    Exporting one page of a filtered view is the kind of thing nobody notices
    until a report is wrong, so this deliberately ignores pagination.
    """
    students = filtered_students(read_filters(request.GET))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)
    writer.writerow(['Last name', 'First name', 'Course', 'Gender', 'Age'])
    for student in students.iterator():
        writer.writerow([
            student.last_name,
            student.first_name,
            student.get_course_display(),
            student.get_gender_display(),
            student.age,
        ])
    return response


@login_required
def student_detail(request, pk):
    """A single record, and the canonical URL for one.

    The edit form already shows every field, so this is not about seeing the
    data - it is about having an address for a student that is not an edit
    form. A link you can send someone, or land on from a search, without
    putting them one mis-click away from changing the record.
    """
    student = get_object_or_404(StudentRecord, pk=pk)
    return render(request, 'student_detail.html', {
        'title': student.full_name,
        'student': student,
    })


@login_required
def student_add(request):
    form = StudentRecordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        student = form.save()
        messages.success(request, f'Added {student.full_name}.')
        return redirect('students:list')

    return render(request, 'student_form_add.html', {
        'title': 'Add student',
        'form': form,
    })


@login_required
def student_update(request, pk):
    student = get_object_or_404(StudentRecord, pk=pk)
    form = StudentRecordForm(request.POST or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Saved {student.full_name}.')
        return redirect('students:list')

    return render(request, 'student_form_update.html', {
        'title': 'Edit student',
        'form': form,
        'student': student,
    })


@login_required
def student_delete(request, pk):
    """Confirm on GET, delete on POST.

    The original handled this inside the list view on POST, looking the record
    up with a bare objects.get() - which returns a 500 on any stale primary
    key, the ordinary result of a double-click or a back button.

    GET rendering a confirmation page replaces the browser confirm() the
    redesign shipped with. confirm() does nothing with JavaScript disabled and
    cannot show what is about to be lost; a real page can, and needs no script.
    """
    student = get_object_or_404(StudentRecord, pk=pk)

    if request.method == 'POST':
        name = student.full_name
        student.delete()
        messages.success(request, f'Deleted {name}.')
        return redirect(_safe_next(request.POST.get('next')))

    return render(request, 'student_confirm_delete.html', {
        'title': 'Delete student',
        'student': student,
        'next': _safe_next(request.GET.get('next')),
    })


@login_required
def student_bulk_delete(request):
    """Delete several records at once, behind the same confirmation step."""
    ids = request.POST.getlist('selected')
    students = StudentRecord.objects.filter(pk__in=ids)
    next_url = _safe_next(request.POST.get('next'))

    if request.method != 'POST':
        return redirect('students:list')

    if not students.exists():
        messages.error(request, 'No records were selected.')
        return redirect(next_url)

    if request.POST.get('confirm') == 'yes':
        count = students.count()
        students.delete()
        messages.success(
            request, f'Deleted {count} record{"" if count == 1 else "s"}.'
        )
        return redirect(next_url)

    return render(request, 'student_confirm_bulk_delete.html', {
        'title': 'Delete students',
        'students': students,
        'count': students.count(),
        'next': next_url,
    })


def _safe_next(value):
    """Only ever redirect within this site.

    `next` comes from the query string, so without this an attacker could hand
    someone a delete link that bounces them to another host afterwards.
    """
    if value and value.startswith('/') and not value.startswith('//'):
        return value
    return '/'
