// Smoke tests for Milestone 1.
//
// This milestone has no JavaScript, so there is no behaviour to exercise —
// what these checks defend is that the pages still render self-contained:
// every stylesheet, image and internal link resolves inside the repo, and
// nothing reaches out to the live SIS or carries a real student's record.
// Run with `npm test`.

import { chromium } from 'playwright';
import { fileURLToPath } from 'node:url';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const url = p => 'file://' + path.join(ROOT, p);

const PAGES = ['index.html', 'pages/submit-grades.html', 'pages/course-list.html'];

let failures = 0;
const ok = (name, cond, detail = '') => {
  console.log(`  ${cond ? 'ok  ' : 'FAIL'}  ${name}${detail ? ' — ' + detail : ''}`);
  if (!cond) failures++;
};

const browser = await chromium.launch();
await (await browser.newPage()).close();   // cold-start, so the first check isn't racing it

console.log('\nevery page loads clean');
for (const file of PAGES) {
  const page = await browser.newPage();
  const errors = [];
  const missing = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push(String(e)));
  page.on('requestfailed', r => {
    if (r.url().startsWith('file://' + ROOT + '/')) missing.push(r.url());
  });
  await page.goto(url(file), { waitUntil: 'load' });
  await page.waitForLoadState('networkidle');
  ok(file, errors.length === 0 && missing.length === 0,
     errors[0] || missing.map(m => path.basename(m)).join(', '));
  await page.close();
}

console.log('\nnavigation resolves');
{
  const page = await browser.newPage();
  await page.goto(url('index.html'));
  for (const [label, expected] of [['View Grades', 'index.html'],
                                   ['Submit Grades', 'pages/submit-grades.html'],
                                   ['CourseList', 'pages/course-list.html']]) {
    const href = await page.locator(`.menu a:has-text("${label}")`).first().getAttribute('href');
    ok(`"${label}" -> ${expected}`, href === expected, `got ${href}`);
    ok(`${expected} exists`, existsSync(path.join(ROOT, expected)));
  }
  await page.close();
}

console.log('\nself-contained and scrubbed');
{
  const html = PAGES.map(f => readFileSync(path.join(ROOT, f), 'utf8')).join('\n');

  // Two icons used to be re-fetched from the university's servers on every load.
  ok('no assets hotlinked from the live SIS',
     !/(src|url\()\s*=?\s*["']?https?:\/\/sis\.addu\.edu\.ph/.test(html));

  // The pages were built by mirroring a live session, so they shipped a real
  // student's record. Asserted positively — listing the real values here would
  // only republish the thing this check exists to keep out.
  const PLACEHOLDER_NAME = 'DELA CRUZ, JUAN PABLO  SANTOS';
  ok('student name is the placeholder', readFileSync(path.join(ROOT, 'index.html'), 'utf8')
       .includes(PLACEHOLDER_NAME));
  for (const [label, value] of [['student code', '000000'], ['RGC number', '00000000']]) {
    ok(`${label} is zeroed`, html.includes(`>${value}<`));
  }
  // Any other long digit run in the header block would be a leftover identifier.
  const header = html.match(/<strong>RGC No:[\s\S]{0,400}/g)?.join('') ?? '';
  ok('no stray identifiers near the record header',
     !/>\d{5,}</.test(header.replace(/>0+</g, '><')));

  // Drupal CSRF tokens captured from that same session.
  ok('Drupal form tokens redacted',
     !/name="form_(build_id|token)" value="(?!REDACTED)[^"]+"/.test(html));

  // 157 inline style attributes were extracted into assets/css/app.css. If one
  // creeps back in, the separation quietly rots.
  ok('no inline style attributes remain', !/\sstyle="/.test(html));
  for (const f of PAGES) {
    const src = readFileSync(path.join(ROOT, f), 'utf8');
    const prefix = f.includes('/') ? '../' : '';
    ok(`${f} links app.css`, src.includes(`href="${prefix}assets/css/app.css"`));
  }

  // The stylesheets are the live site's; they must at least all be present.
  const css = readdirSync(path.join(ROOT, 'assets/css/vendor')).filter(f => f.endsWith('.css'));
  ok('all five vendor stylesheets present', css.length === 5, `${css.length} found`);
  ok('vendor provenance is documented',
     existsSync(path.join(ROOT, 'assets/css/vendor/README.md')));
}

await browser.close();
console.log(`\n${failures === 0 ? 'all checks passed' : failures + ' check(s) failed'}\n`);
process.exit(failures === 0 ? 0 : 1);
