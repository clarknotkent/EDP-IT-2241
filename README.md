# Milestone 2 — DOM events and dynamic tables

> **Archived coursework.** IT 2241 *Event-Driven Programming*, Ateneo de Davao University.
> Built **April 2024**.
>
> **Related:** [`archive/milestone-1`](../../tree/archive/milestone-1) · [`main`](../../tree/main)

---

## What this is

Milestone 1 rebuilt the university's SIS as static pages. Milestone 2 makes them respond:
adding rows to a table from a form, and filtering that table live as you type. No backend,
no persistence — everything lives in the DOM until you reload. That was the assignment.

| Page | Behaviour |
|------|-----------|
| `index.html` | My Grades — presentation only, carried over from Milestone 1 |
| `pages/submit-grades.html` | Encode a grade; the row appends to the class list |
| `pages/course-list.html` | Add a curriculum subject; filter the table per column |
| `prototypes/grade-sheet.html` | Standalone sandbox for the grade table + filters |
| `prototypes/roster.html` | Standalone sandbox for a person roster + filters |
| `prototypes/tailwind-restyle.html` | Milestone 1's grade page redone in Tailwind |

## Running it

No build step and no server required — open `index.html` in a browser.

```bash
git checkout archive/milestone-2
open index.html          # macOS;  xdg-open on Linux,  start on Windows
```

To confirm the interactive pages actually work:

```bash
npm install && npm test
```

That drives all six pages in headless Chromium and asserts the add-row and filter
behaviour on each, plus zero console errors and no unresolved assets.

## Layout

```
.
├── index.html                  # My Grades — the landing page, kept at the root
├── pages/
│   ├── submit-grades.html
│   └── course-list.html
├── assets/
│   ├── css/
│   │   ├── app.css             # our styles, extracted from 181 inline attributes
│   │   ├── tailwind.min.css    # purged local build, 13 KB
│   │   └── vendor/             # the live site's stylesheets
│   ├── img/
│   └── js/   submit-grades.js  course-list.js
├── prototypes/                 # the dt/ sandbox, renamed for what each file is
├── tests/
│   ├── verify.mjs              # npm test
│   └── screenshot.mjs          # npm run shots
├── docs/screenshots/
└── package.json  .gitignore  .editorconfig
```

`index.html` stays at the root so it opens on a double-click and works as a GitHub Pages
entry point; only the secondary pages are grouped. Same layout as
[`archive/milestone-1`](../../tree/archive/milestone-1), so the two are directly comparable.

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
