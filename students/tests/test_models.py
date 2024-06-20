from django.core.exceptions import ValidationError
from django.test import TestCase

from students.models import StudentRecord


class StudentRecordTests(TestCase):
    def make(self, **kwargs):
        defaults = {
            'first_name': 'Ana', 'last_name': 'Cruz',
            'course': 'BS-IT', 'gender': 'F', 'age': 20,
        }
        return StudentRecord(**{**defaults, **kwargs})

    def test_str_is_last_comma_first(self):
        self.assertEqual(str(self.make()), 'Cruz, Ana')

    def test_full_name(self):
        self.assertEqual(self.make().full_name, 'Ana Cruz')

    def test_display_helpers_expand_the_codes(self):
        student = self.make()
        self.assertEqual(student.get_gender_display(), 'Female')
        self.assertEqual(student.get_course_display(), 'BS Information Technology')

    def test_age_upper_bound(self):
        # The submitted database contained a record entered as aged 444.
        with self.assertRaises(ValidationError):
            self.make(age=444).full_clean()

    def test_age_lower_bound(self):
        with self.assertRaises(ValidationError):
            self.make(age=0).full_clean()

    def test_age_within_bounds_is_valid(self):
        self.make(age=21).full_clean()  # must not raise

    def test_unknown_course_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.make(course='BS-XX').full_clean()

    def test_default_ordering_is_by_name(self):
        StudentRecord.objects.create(**{**self.kwargs(), 'last_name': 'Zamora'})
        StudentRecord.objects.create(**{**self.kwargs(), 'last_name': 'Abad'})
        StudentRecord.objects.create(**{**self.kwargs(), 'last_name': 'Marcos'})
        self.assertEqual(
            [s.last_name for s in StudentRecord.objects.all()],
            ['Abad', 'Marcos', 'Zamora'],
        )

    def kwargs(self):
        return {
            'first_name': 'Ana', 'last_name': 'Cruz',
            'course': 'BS-IT', 'gender': 'F', 'age': 20,
        }
