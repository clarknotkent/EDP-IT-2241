"""Query-building shared by the list, the CSV export and the bulk actions.

All three need the same filtered, sorted queryset. Keeping it in one place is
what stops the export quietly disagreeing with the table it was exported from.
"""
from django.db.models import Q

from students.models import StudentRecord

# Only these columns may be sorted on. Sorting is a user-supplied string going
# straight into order_by, so it is a whitelist rather than a sanity check.
SORT_FIELDS = {
    'name': ('last_name', 'first_name'),
    'course': ('course', 'last_name'),
    'gender': ('gender', 'last_name'),
    'age': ('age', 'last_name'),
}
DEFAULT_SORT = 'name'


def read_filters(params):
    """Pull the filter values out of a QueryDict, normalised."""
    sort = params.get('sort', DEFAULT_SORT)
    if sort not in SORT_FIELDS:
        sort = DEFAULT_SORT
    return {
        'search': params.get('search', '').strip(),
        'courses': params.getlist('course'),
        'gender': params.get('gender', 'all'),
        'min_age': params.get('min_age', '').strip(),
        'max_age': params.get('max_age', '').strip(),
        'sort': sort,
        'dir': 'desc' if params.get('dir') == 'desc' else 'asc',
    }


def filtered_students(filters):
    students = StudentRecord.objects.all()

    if filters['search']:
        students = students.filter(
            Q(first_name__icontains=filters['search'])
            | Q(last_name__icontains=filters['search'])
        )
    if filters['courses']:
        students = students.filter(course__in=filters['courses'])
    if filters['gender'] != 'all':
        students = students.filter(gender=filters['gender'])

    # A non-numeric min_age would raise ValueError deep inside the ORM and
    # return a 500; an ignored one just shows more rows than asked for.
    for key, lookup in (('min_age', 'age__gte'), ('max_age', 'age__lte')):
        value = filters[key]
        if value.isdigit():
            students = students.filter(**{lookup: int(value)})

    fields = SORT_FIELDS[filters['sort']]
    if filters['dir'] == 'desc':
        fields = tuple(f'-{f}' for f in fields)
    return students.order_by(*fields)


def is_filtered(filters):
    return bool(
        filters['search']
        or filters['courses']
        or filters['gender'] != 'all'
        or filters['min_age']
        or filters['max_age']
    )
