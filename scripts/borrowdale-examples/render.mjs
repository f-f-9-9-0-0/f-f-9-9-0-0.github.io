// Renders the chart examples shown on the BorrowdaleJS project page.
// The figures are illustrative, not real measurements. Run from this directory:
//   npm ci && npx playwright-core install chromium && npm run render
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { layoutChart, toSvgChart } from '@borrowdale/charts';
import { excalifontFiles } from '@borrowdale/text/excalifont-files';
import { chromium } from 'playwright-core';

const output = join(dirname(fileURLToPath(import.meta.url)), '../../assets/images/projects/borrowdalejs');

const charts = {
  'sketchbook-sales': {
    width: 640,
    height: 320,
    seed: 'sketchbook',
    title: 'Sketchbook sales by month',
    axes: {
      x: { type: 'band', categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] },
      y: { type: 'linear', title: 'Books sold' },
    },
    series: [
      { type: 'bar', name: 'Pocket', stack: 'books', data: [42, 48, 51, 60, 58, 66] },
      { type: 'bar', name: 'A4', stack: 'books', data: [30, 28, 35, 38, 44, 47] },
      { type: 'line', name: 'Target', curve: 'monotone', dash: [6, 4], data: [70, 75, 80, 90, 95, 105] },
    ],
  },
  'pencil-grades': {
    width: 480,
    height: 360,
    seed: 'graphite',
    title: 'Pencils in the drawer',
    legend: 'right',
    series: [
      {
        type: 'pie',
        name: 'Grade',
        innerRadius: 0.5,
        padAngle: 2,
        data: [
          { name: '2H', value: 4 },
          { name: 'HB', value: 11 },
          { name: '2B', value: 8 },
          { name: '4B', value: 5 },
          { name: '8B', value: 2 },
        ],
      },
    ],
  },
  'club-committee': {
    width: 560,
    height: 340,
    seed: 'seats',
    title: 'Sketching club committee',
    series: [
      {
        type: 'units',
        name: 'Seats',
        display: 'parliament',
        data: [
          { name: 'Ink', value: 9 },
          { name: 'Graphite', value: 14 },
          { name: 'Charcoal', value: 6 },
          { name: 'Watercolour', value: 11 },
        ],
      },
    ],
  },
  'studio-visits': {
    width: 560,
    height: 340,
    seed: 'studio',
    title: 'Studio visits by day and hour',
    colorAxis: { type: 'linear', title: 'Visitors' },
    axes: {
      x: { type: 'band', categories: ['9am', '11am', '1pm', '3pm', '5pm'] },
      y: { type: 'band', categories: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
    },
    series: [
      {
        type: 'heatmap',
        name: 'Visitors',
        data: [
          ['9am', 'Mon', 2], ['11am', 'Mon', 5], ['1pm', 'Mon', 7], ['3pm', 'Mon', 4], ['5pm', 'Mon', 1],
          ['9am', 'Tue', 3], ['11am', 'Tue', 6], ['1pm', 'Tue', 9], ['3pm', 'Tue', 6], ['5pm', 'Tue', 2],
          ['9am', 'Wed', 1], ['11am', 'Wed', 4], ['1pm', 'Wed', 8], ['3pm', 'Wed', 7], ['5pm', 'Wed', 3],
          ['9am', 'Thu', 4], ['11am', 'Thu', 8], ['1pm', 'Thu', 12], ['3pm', 'Thu', 9], ['5pm', 'Thu', 5],
          ['9am', 'Fri', 2], ['11am', 'Fri', 3], ['1pm', 'Fri', 6], ['3pm', 'Fri', 10], ['5pm', 'Fri', 8],
        ],
      },
    ],
  },
};

// The charts draw dark ink on a transparent ground, which the site's dark theme would swallow.
// A paper-coloured rectangle goes behind the marks, after the <title> that names the drawing.
// The embedded Excalifont travels with each file, so its licence notice does too (SIL OFL 1.1).
const rootTitle = /^<svg [^>]*><title>[^<]*<\/title>/;
const fontNotice = '<!-- Labels set in Excalifont, copyright 2024 Excalidraw, licensed under the SIL Open '
  + 'Font License 1.1 (https://openfontlicense.org). Excalifont is a trademark of Excalidraw. -->';

function onPaper(svg) {
  const head = rootTitle.exec(svg);
  if (head === null) {
    throw new Error('Unexpected SVG output: expected an <svg> element whose first child is its <title>');
  }
  const rest = svg.slice(head[0].length);
  return head[0] + fontNotice + '<rect width="100%" height="100%" fill="#fffdf7"/>' + rest;
}

function render(name, spec) {
  const layout = layoutChart(spec);
  // A character outside the embedded font would be drawn in a fallback font, off its measured width.
  if (layout.missing.length > 0) {
    throw new Error(`${name}: the font has no glyph for ${JSON.stringify(layout.missing)}`);
  }
  return onPaper(toSvgChart(layout, { fontFiles: excalifontFiles }));
}

// Everything is produced in memory first, so a failure leaves the committed files as they were.
const files = Object.entries(charts).map(([name, spec]) => [`${name}.svg`, render(name, spec) + '\n']);

// Link previews need a raster image at 1200 by 630, and most platforms ignore SVG. The first
// chart is laid out at half that size and photographed at twice the pixel density.
const preview = render('social-preview', { ...charts['sketchbook-sales'], width: 600, height: 315 });
const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 600, height: 315 }, deviceScaleFactor: 2 });
  await page.setContent(`<!doctype html><body style="margin:0">${preview}</body>`);
  await page.evaluate(() => document.fonts.ready);
  files.push(['social-preview.png', await page.locator('svg').screenshot()]);
} finally {
  await browser.close();
}

mkdirSync(output, { recursive: true });
for (const [name, content] of files) {
  writeFileSync(join(output, name), content);
  console.log(name);
}
