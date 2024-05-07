// Smoke tests for Milestone 2.
//
// Every assertion here corresponds to a bug that was live in the original
// submission. Four of the five were visible as a red console error on page
// load; none of them were caught, because nobody opened the console. Run with
// `npm test`.

import { chromium } from 'playwright';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const url = p => 'file://' + path.join(ROOT, p);

const PAGES = [
  'index.html',
  'pages/submit-grades.html',
  'pages/course-list.html',
  'prototypes/grade-sheet.html',
  'prototypes/roster.html',
  'prototypes/tailwind-restyle.html',
];

let failures = 0;
const ok = (name, cond, detail = '') => {
  console.log(`  ${cond ? 'ok  ' : 'FAIL'}  ${name}${detail ? ' — ' + detail : ''}`);
  if (!cond) failures++;
};

async function openPage(browser, file) {
  const page = await browser.newPage();
  const errors = [];
  const missing = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push(String(e)));
  // Only count assets this repo actually ships. A browser may probe for things
  // like /favicon.ico on a cold profile, which says nothing about our markup.
  page.on('requestfailed', r => {
    if (r.url().startsWith('file://' + ROOT + '/')) missing.push(r.url());
  });
  await page.goto(url(file), { waitUntil: 'load' });
  await page.waitForLoadState('networkidle');
  return Object.assign(page, { errors, missing });
}

const browser = await chromium.launch();

// Cold-start the browser once so the first real assertion isn't racing it.
await (await browser.newPage()).close();

// Regression: four separate load-time exceptions used to live here.
console.log('\nevery page loads clean');
for (const file of PAGES) {
  const page = await openPage(browser, file);
  ok(file, page.errors.length === 0 && page.missing.length === 0,
     page.errors[0] || page.missing.map(m => path.basename(m)).join(', '));
  await page.close();
}

// Regression: <form id="myForm"> was nested inside <form id="view-grade-form">,
// so the element never existed and the script threw on load.
console.log('\npages/submit-grades.html — add a row');
{
  const page = await openPage(browser, 'pages/submit-grades.html');
  ok('form#myForm survives parsing', await page.locator('form#myForm').count() === 1);
  for (const [id, v] of [['code', '202020'], ['sname', 'TESTER, ONE'], ['gtype', 'NEW'],
                         ['ylvl', '2'], ['astatus', 'Regular'], ['yentry', '2022'], ['elvl', '1']]) {
    await page.fill(`#${id}`, v);
  }
  await page.selectOption('#final', 'A');
  await page.locator('form#myForm button[type="submit"]').first().click();
  ok('row appended', await page.locator('#tableBody tr').count() === 1);
  ok('row carries the submitted values',
     (await page.locator('#tableBody tr').last().textContent()).includes('TESTER, ONE'));
  await page.close();
}

// Regression: this page had no <script> tag at all, and its curriculum rows
// were commented out.
console.log('\npages/course-list.html — add and filter');
{
  const page = await openPage(browser, 'pages/course-list.html');
  const seeded = await page.locator('#tableBody tr').count();
  ok('curriculum rows are live', seeded === 10, `${seeded} rows`);

  for (const [id, v] of [['ylvl', '2nd Yr.'], ['sem', '1st Semester'], ['subno', 'IT 2241'],
                         ['dtitle', 'EVENT-DRIVEN PROGRAMMING'], ['units', '3']]) {
    await page.fill(`#${id}`, v);
  }
  await page.click('#addRowButton');
  ok('row appended', await page.locator('#tableBody tr').count() === seeded + 1);
  ok('inputs cleared after add', (await page.inputValue('#subno')) === '');

  await page.fill('#search-dtitle', 'event-driven');
  ok('per-column filter narrows to the match',
     await page.locator('#tableBody tr:visible').count() === 1);
  await page.fill('#search-dtitle', '');
  ok('clearing the filter restores every row',
     await page.locator('#tableBody tr:visible').count() === seeded + 1);

  await page.fill('#ylvl', '');
  await page.click('#addRowButton');
  ok('a missing required field is rejected',
     await page.locator('#tableBody tr').count() === seeded + 1);
  await page.close();
}

// Regression: referenced filterGenderInputs / minAgeInput which it never
// declared, and filtered on the roster's column order rather than its own.
console.log('\nprototypes/grade-sheet.html — filters match the columns');
{
  const page = await openPage(browser, 'prototypes/grade-sheet.html');
  ok('no Gender control (this table has no gender column)',
     await page.locator('input[name="filterGender"]').count() === 0);

  const add = async (code, name, gtype, ylvl, astatus) => {
    for (const [id, v] of [['code', code], ['sname', name], ['gtype', gtype],
                           ['ylvl', ylvl], ['astatus', astatus], ['yentry', '2022'], ['elvl', '1']]) {
      await page.fill(`#${id}`, v);
    }
    await page.selectOption('#final', 'A');
    await page.click('#myForm button[type="submit"]');
  };
  await add('111', 'ALPHA, ANA', 'NEW', '2', 'Regular');
  await add('222', 'BRAVO, BEN', 'OLD', '3', 'Irregular');
  ok('two rows added', await page.locator('#tableBody tr').count() === 2);

  await page.check('input[name="filterGradeType"][value="old"]');
  ok('grade-type filter', await page.locator('#tableBody tr:visible').count() === 1);
  await page.check('input[name="filterGradeType"][value="all"]');

  await page.selectOption('#filterYearLevel', '2');
  ok('year-level filter', await page.locator('#tableBody tr:visible').count() === 1);
  await page.selectOption('#filterYearLevel', 'all');

  await page.fill('#search', 'bravo');
  ok('name search', await page.locator('#tableBody tr:visible').count() === 1);
  await page.close();
}

// Regression: loaded datatable.js, whose field ids do not exist on this page.
console.log('\nprototypes/roster.html — loads its own script');
{
  const page = await openPage(browser, 'prototypes/roster.html');
  await page.fill('#firstName', 'Ana');
  await page.fill('#lastName', 'Cruz');
  await page.check('input[name="gender"][value="female"]');
  await page.fill('#age', '20');
  await page.selectOption('#position', { index: 1 });
  await page.click('#myForm button[type="submit"]');
  ok('row appended', await page.locator('#tableBody tr').count() === 1);
  ok('first and last name concatenated',
     (await page.locator('#tableBody tr').first().textContent()).includes('Ana Cruz'));
  await page.check('input[name="filterGender"][value="male"]');
  ok('gender filter hides the row',
     await page.locator('#tableBody tr:visible').count() === 0);
  await page.close();
}

// Regression: 181 inline style attributes were extracted into assets/css/app.css.
console.log('\nstyles stay out of the markup');
{
  const { readFileSync, existsSync } = await import('node:fs');
  const html = PAGES.concat(['prototypes/tailwind-restyle.html'])
    .map(f => readFileSync(path.join(ROOT, f), 'utf8')).join('\n');
  ok('no inline style attributes remain', !/\sstyle="/.test(html));
  ok('app.css exists', existsSync(path.join(ROOT, 'assets/css/app.css')));
}

await browser.close();
console.log(`\n${failures === 0 ? 'all checks passed' : failures + ' check(s) failed'}\n`);
process.exit(failures === 0 ? 0 : 1);
