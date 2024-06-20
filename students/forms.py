from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

from students.models import StudentRecord

# The widget classes live here because Django renders the inputs, not the
# template. Width is per-field and the border is chosen per state, so no two
# border-width utilities ever land on the same element and race.
FIELD_BASE = (
    'h-11 md:h-10 px-2.5 bg-white text-base md:text-sm text-slate-900 '
    'placeholder:text-slate-400 '
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900 '
    'focus-visible:ring-offset-2 '
    'dark:bg-slate-950 dark:text-slate-100 dark:focus-visible:ring-slate-300 '
    'dark:focus-visible:ring-offset-slate-900'
)
BORDER_OK = 'border border-slate-300 dark:border-slate-700'
BORDER_ERROR = 'border-2 border-red-700 dark:border-red-500'
RADIO_CLASSES = (
    'h-4 w-4 shrink-0 accent-slate-900 dark:accent-slate-300 '
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900 '
    'focus-visible:ring-offset-2 dark:focus-visible:ring-slate-300 '
    'dark:focus-visible:ring-offset-slate-900'
)


class StudentRecordForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # A ModelForm adds a blank choice to a field with choices, which on a
        # RadioSelect renders as a preselected "---------" radio button. A
        # required radio group should have nothing selected until the user picks.
        self.fields['gender'].choices = StudentRecord.GENDER_CHOICES

        # Colour is never the only signal - the field also gains aria-invalid
        # and points at the message the template renders below it.
        for name, field in self.fields.items():
            widget = field.widget
            if not (self.is_bound and self.errors.get(name)):
                continue
            widget.attrs['aria-invalid'] = 'true'
            widget.attrs['aria-describedby'] = f'{name}-error'
            if not isinstance(widget, forms.RadioSelect):
                widget.attrs['class'] = (
                    widget.attrs.get('class', '').replace(BORDER_OK, '').strip()
                    + ' '
                    + BORDER_ERROR
                )

    class Meta:
        model = StudentRecord
        fields = ['first_name', 'last_name', 'course', 'gender', 'age']
        widgets = {
            'first_name': forms.TextInput(
                attrs={'class': f'{FIELD_BASE} {BORDER_OK} w-full', 'autofocus': True},
            ),
            'last_name': forms.TextInput(
                attrs={'class': f'{FIELD_BASE} {BORDER_OK} w-full'},
            ),
            'course': forms.Select(
                attrs={'class': f'{FIELD_BASE} {BORDER_OK} w-full'},
            ),
            'gender': forms.RadioSelect(attrs={'class': RADIO_CLASSES}),
            'age': forms.NumberInput(
                attrs={'class': f'{FIELD_BASE} {BORDER_OK} w-28', 'min': 1, 'max': 120},
            ),
        }


class StyledAuthenticationForm(AuthenticationForm):
    """AuthenticationForm with the same widget styling as the record form.

    Django's own form carries no widget classes, and a template cannot add one
    to a rendered widget. The alternative is hand-writing the two inputs in
    login.html, which quietly drops whatever Django puts on them - the
    autofocus, the maxlength, and any attribute a future Django adds.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        autocomplete = {'username': 'username', 'password': 'current-password'}
        for name, field in self.fields.items():
            has_error = bool(self.is_bound and self.errors.get(name))
            border = BORDER_ERROR if has_error else BORDER_OK
            field.widget.attrs.update({
                'class': f'{FIELD_BASE} {border} w-full',
                'autocomplete': autocomplete.get(name, 'off'),
            })
            if has_error:
                field.widget.attrs['aria-invalid'] = 'true'
                field.widget.attrs['aria-describedby'] = f'{name}-error'
        self.fields['username'].widget.attrs['autofocus'] = True


class StyledPasswordChangeForm(PasswordChangeForm):
    """PasswordChangeForm with the app's widget styling.

    Same reasoning as StyledAuthenticationForm: Django renders these inputs, so
    the classes cannot come from the template.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        autocomplete = {
            'old_password': 'current-password',
            'new_password1': 'new-password',
            'new_password2': 'new-password',
        }
        for name, field in self.fields.items():
            has_error = bool(self.is_bound and self.errors.get(name))
            border = BORDER_ERROR if has_error else BORDER_OK
            field.widget.attrs.update({
                'class': f'{FIELD_BASE} {border} w-full',
                'autocomplete': autocomplete.get(name, 'off'),
            })
            if has_error:
                field.widget.attrs['aria-invalid'] = 'true'
                field.widget.attrs['aria-describedby'] = f'{name}-error'
        self.fields['old_password'].widget.attrs['autofocus'] = True
