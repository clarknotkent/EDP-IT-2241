# Milestone 3 — EDP-SMS, a Django student management system

> **Archived coursework.** IT 2241 *Event-Driven Programming*, Ateneo de Davao University — built **May 2024**.
>
> **Related:** [`archive/milestone-1`](../../tree/archive/milestone-1) · [`archive/milestone-2`](../../tree/archive/milestone-2)

---

## What this is

The final milestone, and the only one with a real backend. Milestones 1 and 2 mirrored the
university's SIS as static pages and then made them respond to events in the browser;
this one drops the mirror entirely and builds a working CRUD application on Django 5,
with a SQLite database, the Django admin, and server-side search and filtering.

| Component | What it does |
|-----------|--------------|
| `students.StudentRecord` | One model: first/last name, course, gender, age |
| `students.views.students` | List, search by name, filter by course/gender/age range, delete |
| `students.views.add` | Create a record through a `ModelForm` |
| `students.views.update` | Edit an existing record |
| Django admin | Registered with a custom `list_display` |

## Running it

```bash
git checkout archive/milestone-3
cd Django/django1
python -m venv .venv && source .venv/bin/activate
pip install 'Django>=5.0,<5.1'
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open **`http://127.0.0.1:8000/students/students`** — not `/`, which returns 404.
That doubled path is one of the bugs listed below; it is preserved here and fixed on `main`.

There is no `requirements.txt` in this snapshot because there was none in the submission.

## Credits

**IT 2241 — Event-Driven Programming**
2nd Semester, AY 2023–2024 · Ateneo de Davao University
Instructor: Dwight Ian De Jesus

Group project by:

- Kent Elrond Andionne L. Aspa
- Dominic Carlo Bolivar

**Every person in the sample data is fictional.** The coursework was originally built by
mirroring a live SIS session, so it carried real records — a classmate's grades, a class
roster with student numbers, the instructor's own student record. All of it has been
replaced with placeholders or removed. Any resemblance to a real student is a leftover we
would want to know about.
