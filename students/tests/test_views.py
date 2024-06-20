"""View tests.

Several of these are regression tests: they pin down a specific fault that was
live in the May 2024 submission, named in the test's own docstring. The rest
cover behaviour that was correct and should stay that way — the Q-object
filtering in particular, which was the best-written part of the original.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from students.models import StudentRecord


class BaseCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = 'not-a-real-password-123'
        cls.user = User.objects.create_user('staff', 'staff@example.com', cls.password)
        cls.ana = StudentRecord.objects.create(
            first_name='Ana', last_name='Cruz', course='BS-IT', gender='F', age=20)
        cls.ben = StudentRecord.objects.create(
            first_name='Ben', last_name='Diaz', course='BS-CS', gender='M', age=22)
        cls.cy = StudentRecord.objects.create(
            first_name='Cy', last_name='Reyes', course='BS-DS', gender='M', age=25)

    def sign_in(self):
        self.client.login(username='staff', password=self.password)


class RoutingTests(BaseCase):
    """The submission served the app at /students/students and 404'd on /."""

    def test_list_is_at_the_root(self):
        self.sign_in()
        self.assertEqual(self.client.get('/').status_code, 200)

    def test_urls_reverse_through_the_namespace(self):
        self.assertEqual(reverse('students:list'), '/')
        self.assertEqual(reverse('students:add'), '/add/')
        self.assertEqual(reverse('students:update', args=[1]), '/1/edit/')
        self.assertEqual(reverse('students:delete', args=[1]), '/1/delete/')


class FilterTests(BaseCase):
    def setUp(self):
        self.sign_in()

    def get(self, **params):
        return self.client.get(reverse('students:list'), params)

    def test_search_matches_either_name(self):
        self.assertEqual(list(self.get(search='cruz').context['students']), [self.ana])
        self.assertEqual(list(self.get(search='ben').context['students']), [self.ben])

    def test_search_is_case_insensitive(self):
        self.assertEqual(list(self.get(search='CRUZ').context['students']), [self.ana])

    def test_single_course_filter(self):
        self.assertEqual(list(self.get(course='BS-IT').context['students']), [self.ana])

    def test_multiple_course_filter_returns_the_union(self):
        response = self.get(course=['BS-IT', 'BS-CS'])
        self.assertCountEqual(list(response.context['students']), [self.ana, self.ben])

    def test_multiple_course_filter_keeps_every_checkbox_checked(self):
        """Regression.

        base.html tested `{% if course in request.GET.filterCourses %}`, which
        resolves to the LAST value only and then substring-matches it. Selecting
        two courses rendered exactly one checkbox as checked, so the next submit
        silently dropped the other.
        """
        html = self.get(course=['BS-IT', 'BS-CS']).content.decode()
        for code in ('BS-IT', 'BS-CS'):
            self.assertRegex(html, rf'value="{code}"[^>]*checked')
        for code in ('BS-DS', 'BS-IS'):
            self.assertNotRegex(html, rf'value="{code}"[^>]*checked')

    def test_gender_filter(self):
        self.assertEqual(list(self.get(gender='F').context['students']), [self.ana])

    def test_age_range_is_inclusive(self):
        self.assertCountEqual(
            list(self.get(min_age=20, max_age=22).context['students']),
            [self.ana, self.ben],
        )

    def test_filters_compose(self):
        response = self.get(course=['BS-CS', 'BS-DS'], gender='M', min_age=23)
        self.assertEqual(list(response.context['students']), [self.cy])

    def test_no_filters_returns_everything(self):
        self.assertEqual(self.get().context['total'], 3)


class DisplayTests(BaseCase):
    def setUp(self):
        self.sign_in()

    def test_gender_is_rendered_as_a_label(self):
        """Regression: the table printed the raw 'M' / 'F' column value."""
        html = self.client.get(reverse('students:list')).content.decode()
        self.assertIn('Female', html)
        self.assertNotRegex(html, r'<td[^>]*>\s*[MF]\s*</td>')

    def test_empty_state(self):
        html = self.client.get(reverse('students:list'), {'search': 'nobody'}).content.decode()
        self.assertIn('No students match these filters', html)


class AuthTests(BaseCase):
    """Regression: the submission had no authentication at all."""

    def test_list_requires_login(self):
        """The records are staff-only; an anonymous visitor sees nothing at all."""
        response = self.client.get(reverse('students:list'))
        self.assertRedirects(response, '/accounts/login/?next=/')

    def test_list_leaks_no_student_data_to_anonymous_users(self):
        response = self.client.get(reverse('students:list'), follow=True)
        self.assertNotContains(response, 'Cruz')
        self.assertNotContains(response, 'Diaz')

    def test_signed_in_user_sees_the_list(self):
        self.sign_in()
        self.assertEqual(self.client.get(reverse('students:list')).status_code, 200)

    def test_add_requires_login(self):
        response = self.client.get(reverse('students:add'))
        self.assertRedirects(response, '/accounts/login/?next=/add/')

    def test_update_requires_login(self):
        response = self.client.get(reverse('students:update', args=[self.ana.pk]))
        self.assertRedirects(response, f'/accounts/login/?next=/{self.ana.pk}/edit/')

    def test_anonymous_delete_does_not_delete(self):
        self.client.post(reverse('students:delete', args=[self.ana.pk]))
        self.assertTrue(StudentRecord.objects.filter(pk=self.ana.pk).exists())

    def test_signed_in_user_can_reach_the_forms(self):
        self.sign_in()
        self.assertEqual(self.client.get(reverse('students:add')).status_code, 200)
        self.assertEqual(
            self.client.get(reverse('students:update', args=[self.ana.pk])).status_code, 200)


class CreateUpdateTests(BaseCase):
    def setUp(self):
        self.sign_in()

    def test_valid_post_creates_and_redirects(self):
        response = self.client.post(reverse('students:add'), {
            'first_name': 'Dee', 'last_name': 'Santos',
            'course': 'BS-IS', 'gender': 'F', 'age': 19,
        })
        self.assertRedirects(response, reverse('students:list'))
        self.assertTrue(StudentRecord.objects.filter(last_name='Santos').exists())

    def test_invalid_post_creates_nothing_and_shows_errors(self):
        """Regression: fields were wrapped in <th required>, so nothing validated."""
        before = StudentRecord.objects.count()
        response = self.client.post(reverse('students:add'), {
            'first_name': '', 'last_name': '', 'course': '', 'gender': '', 'age': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(StudentRecord.objects.count(), before)
        self.assertContains(response, 'This field is required')

    def test_out_of_range_age_is_rejected_by_the_form(self):
        response = self.client.post(reverse('students:add'), {
            'first_name': 'Old', 'last_name': 'Person',
            'course': 'BS-IT', 'gender': 'M', 'age': 444,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(StudentRecord.objects.filter(last_name='Person').exists())

    def test_update_persists(self):
        self.client.post(reverse('students:update', args=[self.ana.pk]), {
            'first_name': 'Ana', 'last_name': 'Cruz-Reyes',
            'course': 'BS-CS', 'gender': 'F', 'age': 21,
        })
        self.ana.refresh_from_db()
        self.assertEqual(self.ana.last_name, 'Cruz-Reyes')
        self.assertEqual(self.ana.course, 'BS-CS')

    def test_update_renders_the_bound_form(self):
        """Regression: update.html hand-wrote its inputs, dropping the widgets."""
        html = self.client.get(reverse('students:update', args=[self.ana.pk])).content.decode()
        self.assertIn('value="Ana"', html)
        self.assertIn('type="radio"', html)  # gender uses RadioSelect


class DeleteTests(BaseCase):
    def setUp(self):
        self.sign_in()

    def test_post_deletes(self):
        self.client.post(reverse('students:delete', args=[self.ana.pk]))
        self.assertFalse(StudentRecord.objects.filter(pk=self.ana.pk).exists())

    def test_get_shows_a_confirmation_page_and_deletes_nothing(self):
        """GET used to be a flat 405.

        It now renders a confirmation page, which replaced the browser
        confirm() dialog - that did nothing with JavaScript disabled and could
        not show what was about to be lost. The property that matters is
        unchanged and asserted here: a GET must never delete.
        """
        response = self.client.get(reverse('students:delete', args=[self.ana.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete Ana Cruz?')
        self.assertContains(response, 'cannot be undone')
        self.assertTrue(StudentRecord.objects.filter(pk=self.ana.pk).exists())

    def test_stale_pk_is_404_not_500(self):
        """Regression: a bare objects.get() raised DoesNotExist -> 500.

        Reachable by double-clicking Delete, or by going back and clicking again.
        """
        response = self.client.post(reverse('students:delete', args=[999999]))
        self.assertEqual(response.status_code, 404)


class PaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = 'not-a-real-password-123'
        User.objects.create_user('staff', 'staff@example.com', cls.password)
        for i in range(60):
            StudentRecord.objects.create(
                first_name=f'S{i:02}', last_name=f'L{i:02}',
                course='BS-IT' if i % 2 else 'BS-CS',
                gender='MF'[i % 2], age=18 + i % 10)

    def setUp(self):
        self.client.login(username='staff', password=self.password)

    def test_first_page_is_capped(self):
        response = self.client.get(reverse('students:list'))
        self.assertEqual(len(response.context['students']), 25)
        self.assertEqual(response.context['total'], 60)

    def test_last_page_holds_the_remainder(self):
        response = self.client.get(reverse('students:list'), {'page': 3})
        self.assertEqual(len(response.context['students']), 10)

    def test_out_of_range_page_clamps(self):
        response = self.client.get(reverse('students:list'), {'page': 999})
        self.assertEqual(response.status_code, 200)

    def test_filters_survive_page_links(self):
        response = self.client.get(reverse('students:list'), {'course': 'BS-IT', 'page': 2})
        self.assertEqual(response.context['total'], 30)
        self.assertIn('course=BS-IT', response.content.decode())


class LayoutTests(BaseCase):
    """Faults found by rendering the pages, which the behavioural tests missed."""

    def test_filter_sidebar_only_appears_on_the_list(self):
        """The filter form lived in base.html, so /add/ rendered empty
        Course and Gender groups — those loops have no choices there."""
        self.sign_in()
        # id="search" belongs to the filter form only; note that name="course"
        # would be a false negative here, because the add form has a course field.
        self.assertContains(self.client.get(reverse('students:list')), 'id="search"')
        self.assertNotContains(self.client.get(reverse('students:add')), 'id="search"')
        self.assertNotContains(self.client.get(reverse('students:add')), 'type="checkbox"')

    def test_logout_control_is_not_wrapped_in_a_paragraph(self):
        """A <form> inside a <p> is closed early by the parser, breaking the line."""
        self.sign_in()
        html = self.client.get(reverse('students:list')).content.decode()
        header = html[:html.index('Sign out')]
        self.assertNotIn('<p ', header[header.rindex('<div'):])

    def test_gender_radio_group_has_no_blank_option(self):
        """A ModelForm adds a blank choice, which a RadioSelect renders as a
        preselected '---------' radio button."""
        self.sign_in()
        html = self.client.get(reverse('students:add')).content.decode()
        self.assertNotIn('---------</label>', html)
        self.assertNotRegex(html, r'name="gender"[^>]*value=""')


class LoginFormTests(TestCase):
    """The login inputs are Django's widgets, not hand-written HTML."""

    @classmethod
    def setUpTestData(cls):
        cls.password = 'not-a-real-password-123'
        User.objects.create_user('staff', 'staff@example.com', cls.password)

    def test_widgets_carry_the_styling(self):
        html = self.client.get('/accounts/login/').content.decode()
        self.assertIn('name="username"', html)
        self.assertIn('type="password"', html)
        self.assertIn('autocomplete="current-password"', html)

    def test_bad_credentials_report_a_form_level_error_only(self):
        """Django raises a non-field error here on purpose.

        Marking one input invalid would tell an attacker which half they got
        right, so the message names neither field and neither input is flagged.
        """
        response = self.client.post('/accounts/login/',
                                    {'username': 'staff', 'password': 'wrong'})
        html = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')
        self.assertNotIn('aria-invalid="true"', html)

    def test_a_missing_field_is_flagged_on_the_input(self):
        """An empty field IS a per-field error, and should be marked as one."""
        response = self.client.post('/accounts/login/',
                                    {'username': '', 'password': ''})
        html = response.content.decode()
        self.assertIn('aria-invalid="true"', html)
        self.assertIn('border-red-700', html)
        self.assertIn('id="username-error"', html)

    def test_good_credentials_sign_in(self):
        response = self.client.post('/accounts/login/',
                                    {'username': 'staff', 'password': self.password})
        self.assertRedirects(response, reverse('students:list'))


class CountTests(BaseCase):
    """`total` is how many matched; `total_all` is how many exist."""

    def setUp(self):
        self.sign_in()

    def test_unfiltered_counts_agree(self):
        response = self.client.get(reverse('students:list'))
        self.assertEqual(response.context['total'], 3)
        self.assertEqual(response.context['total_all'], 3)

    def test_filtered_view_still_reports_the_full_total(self):
        response = self.client.get(reverse('students:list'), {'course': 'BS-IT'})
        self.assertEqual(response.context['total'], 1)
        self.assertEqual(response.context['total_all'], 3)
        self.assertContains(response, 'matching')
        self.assertContains(response, '3 total')

    def test_empty_state_says_how_many_records_exist(self):
        """A filtered miss must not report that no records exist at all."""
        response = self.client.get(reverse('students:list'), {'search': 'nobody'})
        self.assertContains(response, 'No students match these filters')
        self.assertContains(response, '3 records exist in total')


class PasswordChangeTests(TestCase):
    """Password change is ours; password reset is deliberately absent."""

    @classmethod
    def setUpTestData(cls):
        cls.password = 'not-a-real-password-123'
        User.objects.create_user('staff', 'staff@example.com', cls.password)

    def sign_in(self):
        self.client.login(username='staff', password=self.password)

    def test_requires_login(self):
        response = self.client.get('/accounts/password_change/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_renders_our_own_template_not_the_admin_one(self):
        """Regression.

        include('django.contrib.auth.urls') resolved these views against the
        admin's templates, so the page rendered in Django-admin chrome —
        'Django administration' banner and all — with none of this app's CSS.
        """
        self.sign_in()
        response = self.client.get('/accounts/password_change/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'css/app.css')
        self.assertNotContains(response, 'Django administration')

    def test_changing_the_password_works(self):
        self.sign_in()
        response = self.client.post('/accounts/password_change/', {
            'old_password': self.password,
            'new_password1': 'a-different-password-456',
            'new_password2': 'a-different-password-456',
        })
        self.assertRedirects(response, '/accounts/password_change/done/')
        self.assertTrue(
            self.client.login(username='staff', password='a-different-password-456'))

    def test_password_reset_is_not_routed(self):
        """There is no EMAIL_BACKEND, so a reset form would silently send nothing."""
        for url in ('/accounts/password_reset/', '/accounts/reset/done/'):
            self.assertEqual(self.client.get(url).status_code, 404)


class ChromeTests(BaseCase):
    """Favicon, skip link and the error pages."""

    def test_favicon_is_linked(self):
        """Without it every page load fires a failed /favicon.ico request."""
        self.sign_in()
        self.assertContains(self.client.get(reverse('students:list')), 'rel="icon"')

    def test_skip_link_is_the_first_focusable_element(self):
        self.sign_in()
        html = self.client.get(reverse('students:list')).content.decode()
        body = html[html.index('<body'):]
        self.assertIn('Skip to content', body)
        self.assertLess(body.index('Skip to content'), body.index('Student Records'))
        self.assertIn('id="main"', body)

    def test_404_uses_our_template(self):
        self.sign_in()
        response = self.client.get('/no-such-page/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'Page not found', status_code=404)

    def test_500_template_needs_no_request_context(self):
        """500.html renders with no context processors.

        Anything needing `request` or `user` would fail at exactly the moment
        the site is already failing, so the template must not reference them.
        """
        from django.template.loader import get_template
        rendered = get_template('500.html').render({})
        self.assertIn('Something went wrong', rendered)
        self.assertNotIn('{{', rendered)


class SortTests(BaseCase):
    def setUp(self):
        self.sign_in()

    def names(self, **params):
        response = self.client.get(reverse('students:list'), params)
        return [s.last_name for s in response.context['students']]

    def test_default_is_by_name(self):
        self.assertEqual(self.names(), ['Cruz', 'Diaz', 'Reyes'])

    def test_sort_by_age_both_ways(self):
        self.assertEqual(self.names(sort='age', dir='asc'), ['Cruz', 'Diaz', 'Reyes'])
        self.assertEqual(self.names(sort='age', dir='desc'), ['Reyes', 'Diaz', 'Cruz'])

    def test_sort_by_course(self):
        self.assertEqual(self.names(sort='course', dir='asc'), ['Diaz', 'Reyes', 'Cruz'])

    def test_unknown_sort_field_falls_back_instead_of_erroring(self):
        """`sort` goes into order_by, so it is a whitelist, not a sanity check."""
        self.assertEqual(self.names(sort='password'), ['Cruz', 'Diaz', 'Reyes'])
        self.assertEqual(self.names(sort='../../etc/passwd'), ['Cruz', 'Diaz', 'Reyes'])

    def test_sort_links_carry_the_active_filters(self):
        response = self.client.get(reverse('students:list'), {'gender': 'M', 'sort': 'age'})
        self.assertIn('gender=M', response.context['sort_links']['course']['url'])

    def test_clicking_the_active_column_flips_the_direction(self):
        response = self.client.get(reverse('students:list'), {'sort': 'age', 'dir': 'asc'})
        self.assertIn('dir=desc', response.context['sort_links']['age']['url'])
        self.assertEqual(response.context['sort_links']['age']['aria'], 'ascending')

    def test_sorting_does_not_carry_the_page_number(self):
        response = self.client.get(reverse('students:list'), {'page': '2', 'sort': 'age'})
        self.assertNotIn('page=', response.context['sort_links']['name']['url'])


class ExportTests(BaseCase):
    def test_requires_login(self):
        response = self.client.get(reverse('students:export'))
        self.assertEqual(response.status_code, 302)

    def test_exports_every_matching_row_not_just_the_page(self):
        self.sign_in()
        response = self.client.get(reverse('students:export'))
        body = response.content.decode()
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="students.csv"', response['Content-Disposition'])
        self.assertEqual(len(body.strip().splitlines()), 4)  # header + 3

    def test_export_honours_the_filters(self):
        self.sign_in()
        response = self.client.get(reverse('students:export'), {'course': 'BS-IT'})
        lines = response.content.decode().strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn('Cruz', lines[1])

    def test_export_uses_labels_not_codes(self):
        self.sign_in()
        body = self.client.get(reverse('students:export')).content.decode()
        self.assertIn('BS Information Technology', body)
        self.assertIn('Female', body)
        self.assertNotIn('BS-IT,', body)


class BulkDeleteTests(BaseCase):
    def setUp(self):
        self.sign_in()

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse('students:bulk_delete'),
                                    {'selected': [self.ana.pk]})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(StudentRecord.objects.filter(pk=self.ana.pk).exists())

    def test_confirmation_step_deletes_nothing(self):
        response = self.client.post(reverse('students:bulk_delete'),
                                    {'selected': [self.ana.pk, self.ben.pk]})
        self.assertContains(response, 'Delete 2 records?')
        self.assertEqual(StudentRecord.objects.count(), 3)

    def test_confirmed_delete_removes_exactly_the_selection(self):
        self.client.post(reverse('students:bulk_delete'), {
            'selected': [self.ana.pk, self.ben.pk], 'confirm': 'yes',
        })
        self.assertEqual(
            list(StudentRecord.objects.values_list('pk', flat=True)), [self.cy.pk])

    def test_empty_selection_is_reported_not_ignored(self):
        response = self.client.post(reverse('students:bulk_delete'),
                                    {'selected': []}, follow=True)
        self.assertContains(response, 'No records were selected')
        self.assertEqual(StudentRecord.objects.count(), 3)

    def test_get_does_not_delete(self):
        self.client.get(reverse('students:bulk_delete'),
                        {'selected': [self.ana.pk], 'confirm': 'yes'})
        self.assertEqual(StudentRecord.objects.count(), 3)


class RedirectSafetyTests(BaseCase):
    """`next` comes from the query string, so it must never leave this site."""

    def setUp(self):
        self.sign_in()

    def test_offsite_next_is_ignored_on_delete(self):
        response = self.client.post(
            reverse('students:delete', args=[self.ana.pk]),
            {'next': 'https://example.net/phish'},
        )
        self.assertEqual(response['Location'], '/')

    def test_protocol_relative_next_is_ignored(self):
        response = self.client.post(
            reverse('students:delete', args=[self.ben.pk]),
            {'next': '//example.net/phish'},
        )
        self.assertEqual(response['Location'], '/')

    def test_onsite_next_is_honoured(self):
        response = self.client.post(
            reverse('students:delete', args=[self.cy.pk]),
            {'next': '/?course=BS-IT'},
        )
        self.assertEqual(response['Location'], '/?course=BS-IT')


class TemplateSyntaxLeakTests(BaseCase):
    """No template syntax may survive into a rendered page.

    Django's {# #} comment is single-line only. A multi-line one is not a
    comment at all: it renders verbatim, and any tag-looking text inside it
    becomes real markup. That is exactly how a stray "<form>" written inside a
    comment ended up wrapping — and therefore destroying — the bulk-delete
    form, while every request-level test still passed, because the test client
    does not parse HTML.
    """

    def setUp(self):
        self.sign_in()

    def pages(self):
        yield self.client.get(reverse('students:list'))
        yield self.client.get(reverse('students:list'), {'search': 'nobody'})
        yield self.client.get(reverse('students:add'))
        yield self.client.get(reverse('students:update', args=[self.ana.pk]))
        yield self.client.get(reverse('students:delete', args=[self.ana.pk]))
        yield self.client.get('/accounts/login/')
        yield self.client.get('/accounts/password_change/')

    def test_no_unrendered_template_syntax(self):
        for response in self.pages():
            html = response.content.decode()
            for token in ('{#', '#}', '{%', '{{'):
                self.assertNotIn(token, html, f'{token} leaked into a rendered page')

    def test_forms_are_never_nested(self):
        """A nested form is silently discarded by every browser."""
        import re
        for response in self.pages():
            depth = 0
            for tag in re.findall(r'</?form[^>]*>', response.content.decode()):
                depth += -1 if tag.startswith('</') else 1
                self.assertLessEqual(depth, 1, 'a form is nested inside another form')
            self.assertEqual(depth, 0, 'unbalanced form tags')


class DetailTests(BaseCase):
    def setUp(self):
        self.sign_in()

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('students:detail', args=[self.ana.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_shows_every_field_with_labels_not_codes(self):
        response = self.client.get(reverse('students:detail', args=[self.ana.pk]))
        self.assertContains(response, 'Ana Cruz')
        self.assertContains(response, 'BS Information Technology')
        self.assertContains(response, 'Female')
        self.assertContains(response, '20')

    def test_unknown_pk_is_404(self):
        self.assertEqual(
            self.client.get(reverse('students:detail', args=[999999])).status_code, 404)

    def test_get_absolute_url_points_at_the_record_not_its_edit_form(self):
        """A canonical URL for a student should not be one click from changing it."""
        self.assertEqual(self.ana.get_absolute_url(), f'/{self.ana.pk}/')

    def test_the_list_links_each_name_to_its_record(self):
        response = self.client.get(reverse('students:list'))
        self.assertContains(response, f'href="/{self.ana.pk}/"')

    def test_detail_does_not_shadow_the_other_routes(self):
        """'<int:pk>/' sits above edit and delete; they must still resolve."""
        self.assertEqual(reverse('students:detail', args=[7]), '/7/')
        self.assertEqual(reverse('students:update', args=[7]), '/7/edit/')
        self.assertEqual(reverse('students:delete', args=[7]), '/7/delete/')
        self.assertEqual(
            self.client.get(reverse('students:update', args=[self.ana.pk])).status_code, 200)
