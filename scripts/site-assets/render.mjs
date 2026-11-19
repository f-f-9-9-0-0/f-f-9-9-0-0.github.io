// Renders the site's BorrowdaleJS drawings into assets/images/: the chart examples on the
// BorrowdaleJS project page, each with a phone-sized render, the home page hero, and the topic
// illustration of every article. The figures are illustrative, not real measurements.
// Run from this directory: npm ci && npx playwright-core install chromium && npm run render
//
// Colours: a drawing shown as an image cannot read the page's custom properties, so each file
// carries a <style> that maps the colours it is drawn in to the site's palette, once for light mode
// and once for dark. The values are read from _data/palette.json, the file site.css is built from.
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { layoutChart, toSvgChart } from '@borrowdale/charts';
import { sketch, toSvgDocument, toSvgSketch } from '@borrowdale/core';
import { excalifontFiles } from '@borrowdale/text/excalifont-files';
import { chromium } from 'playwright-core';
import { GRID, ILLUSTRATIONS } from './illustrations.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const images = join(here, '../../assets/images');

// The site's palette, light and dark, with every colour a drawing uses checked to be a hex code.
function readTheme() {
  const theme = JSON.parse(readFileSync(join(here, '../../_data/palette.json'), 'utf8'));
  for (const mode of ['light', 'dark']) {
    for (const name of NAMES) {
      if (!/^#[0-9a-f]{6}$/.test(theme[mode]?.[name])) {
        throw new Error(`_data/palette.json has no ${mode} "${name}" as a six-digit hex code`);
      }
    }
  }
  return theme;
}

// Placeholder colours the drawings are made in. The <style> of each file repaints them.
const PAPER = '#c0ff00';
const ACCENT = '#c0ff01';
const INK = '#c0ff02';
const CORAL = '#c0ff03';
const HAIR = '#c0ff04';
// BorrowdaleJS draws chart text and axes in this ink and the grid in this grey.
const CHART_INK = '#333';
const CHART_GRID = '#c8c8c8';

// Each placeholder and the palette colour it is repainted with.
const REPAINT = [
  [PAPER, 'paper-deep'], [ACCENT, 'brand'], [INK, 'ink'], [CORAL, 'coral'], [HAIR, 'hair'],
  [CHART_INK, 'ink'], [CHART_GRID, 'hair'],
];
const NAMES = [...new Set(REPAINT.map(([, name]) => name))];

// The file declares the colours it uses under their palette names, for light and for dark mode, so
// scripts/check-site.py can compare each one with the palette. Labels get a halo in
// the frame's colour, so they stay legible over the hatching.
function themeStyle(theme) {
  const properties = (mode) => ':root{' + NAMES.map((name) => `--${name}:${theme[mode][name]};`).join('') + '}';
  return '<style>' + properties('light')
    + `@media (prefers-color-scheme:dark){${properties('dark')}}`
    + REPAINT.map(([from, name]) => `[stroke="${from}"]{stroke:var(--${name})}[fill="${from}"]{fill:var(--${name})}`).join('')
    + 'text{fill:var(--ink);stroke:var(--paper-deep);paint-order:stroke;stroke-width:3px;stroke-linejoin:round}</style>';
}

const rootTitle = /^<svg [^>]*><title>[^<]*<\/title>/;
const rootTag = /^<svg [^>]*>/;
const FONT_NOTICE = '<!-- Labels set in Excalifont, copyright 2024 Excalidraw, licensed under the SIL Open '
  + 'Font License 1.1 (https://openfontlicense.org). Excalifont is a trademark of Excalidraw. -->';

// After the root element (and its <title>, which names the drawing): the theme, the font's licence
// where labels embed it, and a paper rectangle, so a chart opened on its own keeps its ground.
function themed(svg, theme, { title = false, paper = false, font = false } = {}) {
  const head = (title ? rootTitle : rootTag).exec(svg);
  if (head === null) {
    throw new Error('Unexpected SVG output: expected an <svg> element' + (title ? ' whose first child is its <title>' : ''));
  }
  const rest = svg.slice(head[0].length);
  return head[0] + themeStyle(theme) + (font ? FONT_NOTICE : '')
    + (paper ? `<rect width="100%" height="100%" fill="${PAPER}"/>` : '') + rest;
}

// The chart examples keep the library's own series colours, so each is the chart its code draws.
const CHARTS = {
  'sketchbook-sales': {
    width: 640,
    height: 320,
    narrow: { width: 360, height: 300 },
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
    narrow: { width: 360, height: 300 },
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
    narrow: { width: 360, height: 280 },
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
    narrow: { width: 360, height: 300 },
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

function renderChart(name, spec) {
  const layout = layoutChart(spec);
  // A character outside the embedded font would be drawn in a fallback font, off its measured width.
  if (layout.missing.length > 0) {
    throw new Error(`${name}: the font has no glyph for ${JSON.stringify(layout.missing)}`);
  }
  return toSvgChart(layout, { fontFiles: excalifontFiles });
}

// The home page hero: a sketch chart with no labels, in the accent, ink and coral.
const HERO = {
  width: 560,
  height: 460,
  seed: 'hero',
  legend: 'none',
  style: { fillStyle: 'cross-hatch', hachureGap: 8, roughness: 0.9, strokeWidth: 1.4 },
  axes: {
    x: { type: 'band', categories: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'], hidden: true },
    y: { type: 'linear', min: 0, hidden: true },
  },
  series: [
    { type: 'bar', name: 'runs', color: CORAL, data: [2, 3, 2.5, 4, 3.5, 5, 4.5, 6, 5, 7, 6.5, 8] },
    { type: 'area', name: 'rows', color: INK, curve: 'monotone', data: [1.5, 2.5, 2, 3.2, 3, 4.2, 3.8, 5, 4.6, 6, 5.6, 7] },
    { type: 'line', name: 'trend', color: ACCENT, curve: 'monotone', data: [1, 1.8, 2.4, 3, 3.6, 4.4, 5, 5.8, 6.4, 7.2, 7.8, 8.6] },
  ],
};

// A topic illustration: its construction lines faint, its subject in the accent, filled parts
// hatched in coral. Dots too small to hatch are filled solid.
function renderIllustration(name, accent) {
  const options = { seed: name, roughness: 1.1, bowing: 1 };
  const draw = ({ filled, ...shape }) => {
    if (!filled) return sketch(shape, { ...options, stroke: ACCENT, strokeWidth: 2.5 });
    const small = shape.kind === 'circle' && shape.diameter <= 12;
    return sketch(shape, {
      ...options,
      stroke: ACCENT,
      strokeWidth: 2.5,
      fill: small ? ACCENT : CORAL,
      fillStyle: small ? 'solid' : 'hachure',
      hachureGap: 7,
      fillWeight: 1.2,
    });
  };
  const body = [
    ...GRID.map((shape) => toSvgSketch(sketch(shape, { ...options, roughness: 0.6, stroke: HAIR, strokeWidth: 1.2 }))),
    ...accent.map((shape) => toSvgSketch(draw(shape))),
  ];
  return toSvgDocument({ width: 640, height: 320, body });
}

const theme = readTheme();
// Everything is produced in memory first, so a failure leaves the committed files as they were.
const files = [];
for (const [name, { narrow, ...spec }] of Object.entries(CHARTS)) {
  const options = { title: true, paper: true, font: true };
  files.push([`projects/borrowdalejs/${name}.svg`, themed(renderChart(name, spec), theme, options)]);
  files.push([`projects/borrowdalejs/${name}-narrow.svg`, themed(renderChart(name, { ...spec, ...narrow }), theme, options)]);
}
// The project card shows the first chart without its words, so it carries no font.
const { narrow: _cardNarrow, title: _cardTitle, ...cardSpec } = CHARTS['sketchbook-sales'];
const card = layoutChart({
  ...cardSpec,
  legend: 'none',
  axes: { x: { ...cardSpec.axes.x, hidden: true }, y: { ...cardSpec.axes.y, hidden: true } },
});
files.push(['projects/borrowdalejs/sketchbook-sales-card.svg', themed(toSvgChart(card, {}), theme, { paper: true })]);
files.push(['hero.svg', themed(toSvgChart(layoutChart(HERO), {}), theme, {})]);
for (const [name, accent] of Object.entries(ILLUSTRATIONS)) {
  files.push([`articles/${name}.svg`, themed(renderIllustration(name, accent), theme, {})]);
}

// Link previews need a raster image at 1200 by 630, and most platforms ignore SVG. The first
// chart is laid out at half that size and photographed in light mode at twice the pixel density.
const { narrow: _, ...first } = CHARTS['sketchbook-sales'];
const preview = themed(renderChart('social-preview', { ...first, width: 600, height: 315 }), theme, { title: true, paper: true, font: true });
const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 600, height: 315 }, deviceScaleFactor: 2, colorScheme: 'light' });
  await page.setContent(`<!doctype html><body style="margin:0">${preview}</body>`);
  await page.evaluate(() => document.fonts.ready);
  files.push(['projects/borrowdalejs/social-preview.png', await page.locator('svg').screenshot()]);
} finally {
  await browser.close();
}

for (const [name, content] of files) {
  mkdirSync(dirname(join(images, name)), { recursive: true });
  writeFileSync(join(images, name), typeof content === 'string' ? content + '\n' : content);
  console.log(name);
}
