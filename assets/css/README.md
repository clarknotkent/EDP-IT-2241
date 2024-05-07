# Stylesheets

| Path | Origin |
|------|--------|
| `tailwind.min.css` | Tailwind CSS 2.2.19, built locally and purged against `prototypes/*.html`. 13 KB. |
| `vendor/sis-theme-*.css` | The live ADDU SIS's own stylesheets — see `vendor/README.md`. |

## Why Tailwind is vendored

The prototypes originally loaded Tailwind from `cdn.jsdelivr.net` — `grade-sheet.html`
and `roster.html` pinned 2.2.4, `tailwind-restyle.html` pinned 2.2.19. That made three
archived pages depend on a third-party CDN staying up, and it meant they rendered
unstyled with no network.

Rebuilding at 2.2.19 with purge enabled produces one 13 KB file covering all three
pages, against 2.9 MB for the full framework. To regenerate after editing markup:

```bash
npm install tailwindcss@2.2.19 postcss@8 autoprefixer@10 postcss-cli@9
NODE_ENV=production npx postcss in.css -o assets/css/tailwind.min.css
```

with `purge.content` pointed at `prototypes/*.html`.
