/** Tailwind build for the Django templates.
 *
 *  The submission vendored Tailwind.min.js — a 368 KB copy of the Play CDN
 *  runtime, which parses the DOM and generates CSS in the browser on every
 *  page load. Tailwind's own documentation says that is for prototyping only.
 *
 *  Rebuild after changing markup:
 *      npm install && npm run build:css
 */
module.exports = {
  content: ['./templates/**/*.html', './students/forms.py'],
  darkMode: 'class',
  theme: { extend: {} },
  plugins: [],
};
