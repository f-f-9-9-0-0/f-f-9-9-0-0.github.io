# Patterns

How this site solves the problems it meets more than once, so the next change reads like what is
already here. Each pattern names its reference implementation. The rules a change must follow are
in [`standards.md`](standards.md).

## Pinned snapshot of shared files

**Problem.** The privacy page generator is maintained elsewhere and copied in. A local edit would
silently fork it.

**Pattern.** A lock file records a SHA-256 per copied file, and the generator refuses to run when a
file no longer matches. Reference: `scripts/privacy-template.lock.json`, verified at the start of
`scripts/configure-privacy.py`.

- Files and lock change together, from one upstream release
  ([`releases.md`](releases.md), "Refreshing the privacy generator").
- Hashes are over bytes. `.gitattributes` forces LF for the bundled generator so a checkout on
  another operating system cannot change them.
- What the site owns stays outside the snapshot: the processing inventory in
  `scripts/privacy-site.json`, and the layout and styles the generated pages are shown in.

## Theme colours, light and dark

**Problem.** Every page, the generated privacy pages and the drawings must agree on one palette, in
light mode and in dark mode, and a drawing shown as an image cannot read the page's styles.

**Pattern.** The palette is data, one set of named colours for light mode and one for dark.
`assets/css/site.css` writes them as custom properties on `:root`, redefined under
`prefers-color-scheme: dark`, and everything else refers to them by name. Reference:
`_data/palette.json` and the top of `assets/css/site.css`.

```json
{
  "light": { "paper": "#f4f6f3", "ink": "#13232a", "brand": "#0d6b68" },
  "dark": { "paper": "#0e1719", "ink": "#e3ece8", "brand": "#5fd1c6" }
}
```

- An inverted band (the footer) sets `.on-ink`, which swaps `--brand` for the accent that keeps
  its contrast on ink. The focus ring follows it.
- The privacy generator reads `--privacy-*` properties, which `site.css` sets from the theme.
- A drawing carries its own `<style>` with both modes, written by the render script from the same
  palette (see "Drawings rendered by the library they show"). `scripts/check-site.py` compares
  every colour a drawing declares with the palette, by name and mode, so a palette change without a
  re-render cannot ship.

## Fonts served from the site

**Problem.** The design uses three typefaces, and loading them from a font service would send every
reader's address to another company.

**Pattern.** A pinned script copies the WOFF2 files and their licences from npm packages, and writes
the `@font-face` rules. Reference: `scripts/site-assets/fonts.mjs`, which writes `assets/fonts/`
and `assets/css/fonts.css`.

- Each face comes in a `latin` and a `latin-ext` file, with the `unicode-range` of its source
  package, so a browser fetches the second only for a page that uses its characters.
- The two faces every page uses first are preloaded in `_layouts/default.html`.
- `scripts/check-site.py` fails on a page whose markup loads from an origin it does not list, so a
  font service `<link>` fails the build. An `@import` inside a stylesheet is not checked.

## One build, draft or published

**Problem.** A pull request must prove the site builds, but must not see the operator's identity
or the analytics token, and must never be mistaken for a publication.

**Pattern.** One expression decides, and every step that differs reads it. Reference:
`.github/workflows/pages.yml`.

```yaml
env:
  PRIVACY_PUBLISH: ${{ github.ref == 'refs/heads/main' && (github.event_name == 'push' || inputs.deploy) && 'true' || 'false' }}
  SITE_OPERATOR_NAME: ${{ github.ref == 'refs/heads/main' && (github.event_name == 'push' || inputs.deploy) && secrets.SITE_OPERATOR_NAME || '' }}
```

- A draft build renders the privacy pages with a fictional identity, a visible draft notice and
  `noindex,nofollow`, and leaves them out of the sitemap. A published build does the opposite.
- `scripts/check-site.py` reads the same `PRIVACY_PUBLISH` value and asserts the matching
  indexing policy, so a draft cannot pass as a publication or the reverse.
- The artifact upload and the `deploy` job carry the same condition.
- A new step that needs a secret copies the whole condition. An empty value must mean "draft",
  never "fail open".

## Public value from a build-time secret

**Problem.** The analytics site token is public once rendered, but it should not sit in the
repository, and a build without it must still work.

**Pattern.** A committed data file holds the empty default. A script overwrites it from the
environment after validating the shape, and the template renders nothing when the value is
empty. Reference: `_data/cloudflare_analytics.json`, `scripts/configure-analytics.py`,
`_includes/cloudflare-analytics.html`.

```liquid
{% assign cloudflare_token = site.data.cloudflare_analytics.token | default: '' | strip %}
{% if jekyll.environment == 'production' and page.analytics != false and cloudflare_token != '' %}
<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='…'></script>
{% endif %}
```

- Three conditions, all required: a production build, a page that has not opted out, a token.
- A malformed token fails the build. It is never rendered.
- Running the script locally rewrites the data file. Do not commit that change.

## Opting a page out

**Problem.** Some pages must not load analytics, must stay out of the sitemap, or must not be
indexed.

**Pattern.** Front matter flags that default to "included", read by the template that owns the
feature: `analytics: false`, `sitemap: false`, `hidden: true`, and `robots` for the indexing
policy. Reference: the generated privacy pages (front matter written by
`scripts/configure-privacy.py`), `sitemap.xml`, `404.html`.

A check then asserts the outcome on the built page rather than trusting the flag: the privacy
pages must contain no beacon, and `404.html` must not be in the sitemap
(`scripts/check-site.py`).

## Generated pages enter Jekyll as source

**Problem.** The privacy pages are produced by a Python generator, but they need the site's
layout, navigation and metadata.

**Pattern.** The generator writes fragments, the wrapper adds front matter and places them in
the source tree, and Jekyll renders them like any other page. Reference:
`scripts/configure-privacy.py`.

- The front matter is one JSON mapping between the `---` lines. JSON is valid YAML, so no YAML
  writer is needed.
- Braces in the generated body are replaced with HTML entities, so text that came from a secret
  cannot be executed as Liquid.
- The output directory (`/privacy/`) is ignored by git, and the wrapper refuses to run when it
  already exists. Generate into a clean tree.

## Check the built site, not the source

**Problem.** A rule about the published page (one `<h1>`, a canonical URL, a working contents
link) can be broken by a post, a layout or a plugin. Checking each source would miss the
combination.

**Pattern.** After `jekyll build`, a script parses every HTML file under `_site` and raises on
the first violation, naming the page. Reference: `scripts/check-design.rb` (structure,
navigation, anchors, canonical URLs, accessibility hooks, post rules, code examples, emoji
shortcodes) and `scripts/check-site.py` (the home and privacy canonical URLs, sitemap, robots,
privacy policy, loaded resources, drawing colours, link-preview images).

```ruby
raise "#{name}: expected one page heading" unless page.css('h1').size == 1
```

- The message is `<page>: <what is wrong>`.
- The check also asserts what must be absent: `scripts`, `docs` and `ANALYTICS.md` must not
  exist in the output.
- Every root-relative link in the header, the footer and `main` must point at a file in `_site`
  (`scripts/check-design.rb`).
- Every page needs a meta description of its own: `_config.yml` leaves the site's `description`
  empty, so a page without one gets none and fails. A post (rendered by the post layout, or whose
  structured data says `BlogPosting`) must also show the intro text under its title, which comes
  only from its own description, and its author's name; the author's page in its structured data
  is on this site (`scripts/check-design.rb`).
- Every page needs a link-preview image, and it is one of the site's own files: a page without one
  of its own shares the site card through `defaults` in `_config.yml`, and a post sets its own
  (`scripts/check-site.py`).
- No emoji shortcode such as `:warning:` is left in a page's text outside code: nothing renders
  them (`scripts/check-design.rb`).
- A new site-wide rule is one more assertion in the script that already walks the pages, not a
  new script.
- `scripts/check-site.py` reads every built page for the resources its markup loads (scripts,
  stylesheets, preloads, icons, images and their `srcset`, frames): a local one must exist in
  `_site`, so a renamed image fails the build instead of shipping a broken figure, and any other
  must come from a listed origin. It also reads every drawing for colours that differ from
  `_data/palette.json`.

## Synthetic publication test

**Problem.** The published variant only builds on `main`, with real secrets. A mistake in it
would first show on the live site.

**Pattern.** Copy the source to a temporary directory, replace the configuration with a synthetic
reviewed one, set fictional values for the secrets, build there, and run the same checks on that
output. Reference: `scripts/test-site-build.py`.

- The copy and its output live in a temporary directory and are never the Pages artifact.
- The fixtures are plainly fictional (`Test operator`, a `.test` address, a token of repeated
  characters), so a leak of the test output could not be mistaken for real data.
- It asserts the positive case the draft build cannot: exactly one beacon on the homepage.

## Drawings rendered by the library they show

**Problem.** The site's drawings, from the chart examples on the BorrowdaleJS page to the topic
illustration of each article, are made with BorrowdaleJS. A screenshot or a hand-edited copy would
drift from what the library draws, and nobody could make it again.

**Pattern.** A small pinned script renders every drawing, and its output is committed. Reference:
`scripts/site-assets/render.mjs`, which writes the chart examples to
`assets/images/projects/borrowdalejs/`, the home page hero to `assets/images/hero.svg`, the
topic illustrations to `assets/images/articles/` and the site card to
`assets/images/social-preview.png`.

- The library version is pinned exactly in `package.json`, with a lockfile, so a re-render
  reproduces the committed files byte for byte until the pin is moved on purpose.
- Every file is produced in memory first and written only when all of them succeeded, so a
  failure leaves the committed images as they were.
- The hero and the illustrations are drawn in placeholder colours, which the `<style>` of each
  file repaints with the palette of `_data/palette.json`, in light and in dark mode. The chart examples keep
  the library's own series colours, so each stays the chart its code draws; only their ink, grid,
  labels and paper follow the theme.
- A topic illustration is a list of shapes in `scripts/site-assets/illustrations.mjs`, drawn shape
  by shape with `sketch()` from `@borrowdale/core`: a grid of faint construction lines shared by
  every illustration, the subject in the accent, filled parts hatched in coral. Its seed is its name, so it is drawn the same way every time.
- Each chart embeds the font files its labels need, so its labels look the same wherever it is
  opened. The script fails if a label uses a character the font does not cover, rather than
  letting the browser substitute another font. The embedded font's licence notice (SIL OFL 1.1)
  travels with every copy.
- Each chart also has a phone render, 360 wide, which `_includes/article-image.html` serves below
  40rem through `<picture>`. The media query is written as `max-width: 39.99rem`, not in range
  syntax, which Safari on iOS parses only from version 16.4 (MDN browser compatibility data, checked
  2026-11-18); an older iPhone would skip the phone render.
- The project card shows the first chart drawn without its words, so the thumbnail carries no
  font.
- The link-preview PNGs are photographed in light mode by headless Chromium at twice the pixel
  density. The project's is the first chart laid out at 600 by 315. The site card
  (`assets/images/social-preview.png`), which every page without an image of its own shares, sets
  the home page's `hero_label`, `title` and `hero_title` from `_config.yml` in the site's fonts
  above the same chart without its title, so it has to be re-rendered by hand when those settings
  change. The card loads the site's `fonts.css` with each file inlined, and the render fails on a
  character that none of a family's files covers.
- A code sample on the page that claims to draw an image must use the same spec as the script,
  seed included. The two are kept in step by hand.

## Important callout

**Problem.** A post is correct for one version of a tool. Readers on another version need to
know before they read on.

**Pattern.** An `aside` at the top of the post, in HTML so it carries a label for assistive
technology. Reference: any post under `_posts/`.

```html
<aside class="callout" aria-label="Important">
    <p>
        <strong class="callout-title">Important</strong>
        This post is created based on the Airflow version 2.10.4!
    </p>
</aside>
```

- The same box titled "Note", with `aria-label="Note"`, carries a caution inside a post.

## Code examples and screenshots

**Problem.** Long code examples and full-size screenshots need to be readable on a narrow screen,
in both colour modes and from the keyboard. The code is part of the article, so it must be in
the page itself, not loaded from another site.

**Pattern.** Code is written into the post inside a figure; a screenshot goes through an include.
Reference: any post with a `code-example` figure, `_includes/article-image.html`.

````markdown
<figure class="code-example" markdown="1">
<figcaption><span class="code-file">dag_example_logging.py</span> <span>Python</span></figcaption>

```python
import pendulum, logging
```

</figure>

{% include article-image.html src="/assets/images/001/dag_docs.png" alt="DAG level docs" %}
````

- The caption names the file and its language. Rouge highlights the code at build time in the
  palette's colours, in both modes (`site.css`, "Rouge's token classes"); a token class it does
  not colour stays in the ink colour.
- `markdown="1"` lets kramdown read the fenced block inside the figure. Without it the fence is
  printed as text, and the build fails on a code example that is not one highlighted block. A
  blank line before and after the figure keeps the source readable.
- The space between the caption's two spans keeps the file name and the language apart where the
  stylesheet does not apply, as in the feed.
- Code that itself contains ```` ``` ```` takes a `~~~~` fence.
- Nothing is embedded from a gist. The github-pages gem adds `jekyll-gist` back whatever
  `_config.yml` lists, so a `{% gist %}` tag still renders; `scripts/check-site.py` fails the page,
  because GitHub is not a listed origin.
- The fence names the lexer, the caption names the language for the reader, and the two may
  differ: a Kibana console request is highlighted as `hocon`, which reads its `#` comments and
  JSON bodies, and captioned "Kibana console".
- Code containing `{{` or `{%`, such as a Jinja template, goes between `{% raw %}` and
  `{% endraw %}`, or Liquid evaluates it.
- A long example scrolls inside its frame, at most 32rem tall. The post layout gives every `<pre>`
  a tabindex, a role and a label, so it can be scrolled from the keyboard.
- The image include frames the image in a figure, links it to its full-size file and uses `alt` as
  the caption unless `caption` is given. Given `narrow`, it serves that file to phones.
- The build fails on a code block in a post that is not keyboard accessible.

## Contents list from headings

**Problem.** Long posts need a table of contents that cannot go stale.

**Pattern.** The post layout derives it from the rendered `<h2 id="…">` elements, and shows it
only when a post has more than three sections. Reference: `_includes/contents.html`. Nothing is
written by hand; the build checks that every entry resolves to exactly one element.
