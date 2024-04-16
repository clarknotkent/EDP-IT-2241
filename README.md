# Milestone 1 — Static recreation of the ADDU SIS

> **Archived coursework.** IT 2241 *Event-Driven Programming*, Ateneo de Davao University.
> Built **March 2024**.
>
> **Related:** [`archive/milestone-2`](../../tree/archive/milestone-2) · [`main`](../../tree/main)

---

## What this is

The first of three milestones. The brief was to reproduce the university's own Student
Information System — `sis.addu.edu.ph`, a Drupal application — as static pages, working
from the rendered site rather than from a spec or a mockup.

Three pages, no JavaScript at all. That was the point: this milestone was about reading an
existing interface and rebuilding its structure in HTML.

| Page | What it reproduces |
|------|--------------------|
| `index.html` | *My Grades* — student header block, per-subject grade table, legend |
| `pages/submit-grades.html` | Faculty grade-encoding sheet with per-student dropdowns |
| `pages/course-list.html` | Full curriculum listing by year and term |

## Running it

No build step and no server required — open `index.html` in a browser.

```bash
git checkout archive/milestone-1
open index.html          # macOS;  xdg-open on Linux,  start on Windows
```

If you would rather serve it over HTTP:

```bash
python3 -m http.server 8000
# http://localhost:8000
```

To confirm the pages are still self-contained:

```bash
npm install && npm test
```

There is no JavaScript here to exercise, so the checks defend what actually
matters for an archive: every stylesheet, image and internal link resolves inside
the repo, nothing reaches out to the live SIS, and no real student record has
crept back in.

## Layout

```
.
├── index.html                  # My Grades — the landing page, kept at the root
├── pages/
│   ├── submit-grades.html      # faculty grade-encoding sheet
│   └── course-list.html        # curriculum listing
├── assets/
│   ├── css/
│   │   ├── app.css             # our styles, extracted from 157 inline attributes
│   │   └── vendor/             # the live site's stylesheets — see the README there
│   └── img/                    # favicon + local SVGs replacing two hotlinked icons
├── tests/
│   ├── verify.mjs              # npm test
│   └── screenshot.mjs          # npm run shots — full-page renders for diffing
├── docs/screenshots/           # regenerated from the scrubbed pages
└── package.json  .gitignore  .editorconfig
```

`index.html` stays at the root so it opens on a double-click and works as a GitHub Pages
entry point; only the secondary pages are grouped.

## Credits

**IT 2241 — Event-Driven Programming**
2nd Semester, AY 2023–2024 · Ateneo de Davao University
Instructor: Dwight Ian De Jesus

Group project by:

- Kent Elrond Andionne L. Aspa
- Dominic Carlo Bolivar

**Every person in the sample data is fictional.** The class list on the grade-encoding
sheet is the invented cast from the original submission, kept as submitted. What the
coursework *also* carried, because it was built by mirroring a live SIS session, was real
records — a classmate's grades, a roster with student numbers, the instructor's own
student record. Those are replaced with placeholders or deleted outright. Any resemblance to a real student is a leftover we
would want to know about.
