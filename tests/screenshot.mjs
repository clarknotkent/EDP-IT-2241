// Full-page screenshots at a fixed viewport, for before/after comparison.
// Usage: node shot.mjs <outDir> <page.html>[:label] ...
import { chromium } from 'playwright';
import path from 'node:path';
import { mkdirSync } from 'node:fs';

const [outDir, ...specs] = process.argv.slice(2);
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });

for (const spec of specs) {
  const [file, label = path.basename(file, '.html')] = spec.split(':');
  await page.goto('file://' + path.resolve(file), { waitUntil: 'load' });
  await page.waitForLoadState('networkidle');
  await page.addStyleTag({ content: '*{animation:none!important;transition:none!important;caret-color:transparent!important}' });
  await page.screenshot({ path: path.join(outDir, label + '.png'), fullPage: true });
  console.log('  shot', label);
}
await browser.close();
