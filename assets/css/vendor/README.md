# Vendor stylesheets — provenance

These five files are **not original work**. They are the stylesheets served by the
live Ateneo de Davao University Student Information System (`sis.addu.edu.ph`,
a Drupal site), saved during the March 2024 lab session and used unmodified so the
recreation would match the original pixel-for-pixel.

They are numbered `1`–`5` because that is the order the browser loaded them in on
the real site, and the cascade depends on that order being preserved.

| File | Size | Original role |
|------|-----:|---------------|
| `sis-theme-1.css` | 7.6 KB | Drupal system/base reset |
| `sis-theme-2.css` | 5.7 KB | Module styles |
| `sis-theme-3.css` | 10.4 KB | Layout grid and regions |
| `sis-theme-4.css` | 22.3 KB | Theme — the bulk of the visual design |
| `sis-theme-5.css` | 9.5 KB | Page-specific overrides |

They are retained here only so this archived coursework still renders as it did when
it was submitted. The coursework being graded was the **HTML structure**, not this CSS.

## The one modification

These files are otherwise byte-for-byte as saved, with a single exception: 53 `url()`
references pointed at absolute paths on the live server — `/misc/throbber-active.gif`,
`/sites/all/themes/sis/images/printer.png`, the jQuery UI sprite sheet and so on. None of
those files exist in this repo, so every page load fired a batch of failed requests and
filled the console with `ERR_FILE_NOT_FOUND`.

Each has been replaced with `none`. They referenced Drupal's own chrome — progress
throbbers, menu tree icons, jQuery UI widget sprites — none of which any page here uses.
