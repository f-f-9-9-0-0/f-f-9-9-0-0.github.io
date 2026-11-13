---
title: BorrowdaleJS
layout: page
section: projects
projects: true
permalink: /projects/borrowdalejs/
date: 2026-11-13 00:00:00
illustration: /assets/images/projects/borrowdalejs/sketchbook-sales.svg
image: /assets/images/projects/borrowdalejs/social-preview.png
seo:
  type: WebPage
tags:
- data-visualization
- javascript
description: BorrowdaleJS draws hand-drawn charts, text and backgrounds that are identical on the server and in every browser. An introduction, examples and the problems behind it.
---
<div class="article-body" markdown="1">

BorrowdaleJS is an open-source JavaScript library for hand-drawn charts, shapes, text and
backgrounds. The marks look sketched, but the scales, labels and values underneath are exact. It is
named after Borrowdale in the English Lake District, where the graphite that started the pencil
industry was found.

It is published on npm as a family of `@borrowdale` packages, released together. The
[website](https://borrowdalejs.com/) has the documentation of each package, a
[playground](https://borrowdalejs.com/playground/) where every example can be edited and run, and
dashboards built on open data. The source is on
[GitHub](https://github.com/borrowdale/borrowdale), under the MIT licence.

## A chart is plain data

A chart is described as data, so it can come straight from JSON. One call lays it out, measuring
every label and choosing the scales and ticks, and another turns the layout into SVG:

<pre tabindex="0" role="region" aria-label="Code example"><code class="language-js">import { layoutChart, toSvgChart } from '@borrowdale/charts';
import { excalifontFiles } from '@borrowdale/text/excalifont-files';

const chart = layoutChart({
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
});

const svg = toSvgChart(chart, { fontFiles: excalifontFiles });
</code></pre>

{% include article-image.html src="/assets/images/projects/borrowdalejs/sketchbook-sales.svg" alt="Stacked bar chart of pocket and A4 sketchbook sales from January to June, with a dashed target line rising from 70 to 105 books, just below the bar tops" caption="The chart this code draws." %}

## Examples

These charts were drawn by the published packages. The figures are made up for the examples.
Each one is a single SVG file with the font files its labels need embedded, so it looks the same
wherever it is opened.

{% include article-image.html src="/assets/images/projects/borrowdalejs/pencil-grades.svg" alt="Donut chart of pencils in a drawer by grade: 2H, HB, 2B, 4B and 8B, with HB the largest share" caption="A donut chart. Each slice is hatched in its own colour." %}

{% include article-image.html src="/assets/images/projects/borrowdalejs/club-committee.svg" alt="Parliament chart of a sketching club committee: 40 seats in rows of arcs, shared by Ink, Graphite, Charcoal and Watercolour" caption="A unit chart, drawn as a parliament." %}

{% include article-image.html src="/assets/images/projects/borrowdalejs/studio-visits.svg" alt="Heatmap of studio visitors by weekday and hour, busiest on Thursday at 1pm" caption="A heatmap with a colour axis." %}

The [playground](https://borrowdalejs.com/playground/) has many more, from gauges and timelines to
candlesticks and calendars.

## The interesting problems

### The same drawing, byte for byte, everywhere

A sketched line is wobbly on purpose, and the wobble comes from randomness. But a chart rendered
on the server has to match the one the browser draws, and a drawing that changes on every render
cannot be tested. So every stroke is seeded: the same input and seed give the same drawing.

Seeding is the easy half. The harder half is that JavaScript engines may compute `Math.sin`,
`Math.cos`, `Math.log` and `Math.exp` slightly differently, and one differing last digit changes a
coordinate in the output. The drawing code therefore never reads the clock, the locale, the time
zone or `Math.random`, and uses its own portable versions of the maths functions. A test guard makes
any forbidden call throw while a reference drawing is made. The test suite then draws every
reference drawing of the core, text and chart packages in Node and in headless Chromium, Firefox
and WebKit, and requires every output to match byte for byte. That covers the V8, SpiderMonkey and JavaScriptCore engines.

### Measuring text without a browser

An axis cannot be sized until its labels are measured, and measuring text usually needs a browser.
BorrowdaleJS measures text from the font data itself, so a chart can be laid out on a server with
no DOM. The browser tests then check that each browser draws every label at exactly the width that
was measured. The SVG output embeds only the font files its labels need.

### Legends that tell the truth

A colour legend that splits values into classes can quietly misstate them. Tied values can leave a
class empty, and a break rounded for display can put a value on the wrong side of its label. The
library rejects classes that tied or nearly equal values would leave empty. A threshold
break must be written exactly in its axis' number format, and the outer labels of a quantize or quantile legend round
outward so that they contain every value.

### Data from anyone, errors that point at the problem

A chart can come from anyone, so every option is checked. Unknown options are rejected, never
ignored, and an error names the exact place in the data that is wrong:

<pre tabindex="0" role="region" aria-label="Error example"><code>Invalid chart: series[2].data[5] must be a number from -1e15 to 1e15 or null, got "5"
</code></pre>

Colours come from the Okabe–Ito palette, which stays distinguishable with the common forms of
colour blindness. When the colours run out, they come round again with a new hachure angle, so
no two series look alike. Beyond those combinations, a series needs a colour of its own.

## Credits

Labels are set in [Excalifont](https://plus.excalidraw.com/excalifont), by Excalidraw, licensed
under the SIL Open Font License 1.1 and bundled with `@borrowdale/text`. Excalifont is a trademark
of Excalidraw. The drawing engine builds on work from rough.js and other projects, credited on the
library's [licence page](https://borrowdalejs.com/license/).

</div>
