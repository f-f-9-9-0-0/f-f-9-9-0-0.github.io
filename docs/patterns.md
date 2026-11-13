# Patterns

How this site solves the problems it meets more than once, so the next change reads like what is
already here. Each pattern names its reference implementation. The rules a change must follow are
in [`standards.md`](standards.md).

## Pinned snapshot of shared files

**Problem.** The presentation (layouts, shared includes, the stylesheet) and the privacy page
generator are maintained elsewhere and copied in. A local edit would silently fork them.

**Pattern.** A lock file records a SHA-256 per copied file, and the build fails when a file no
longer matches. Reference: `scripts/portfolio-template.lock.json` with
`scripts/check-portfolio-template.py`, and `scripts/privacy-template.lock.json`, verified at the
start of `scripts/configure-privacy.py`.

```json
{
  "version": "0.2.0",
  "files": {
    "_layouts/default.html": "7c448cc2…"
  },
  "source_commit": "616ca433…"
}
```

- The check runs first in the workflow, before Ruby is installed, so a drifted file fails in
  seconds.
- Files and lock change together, from one upstream release
  ([`releases.md`](releases.md), "Refreshing the pinned bundles").
- Hashes are over bytes. `.gitattributes` forces LF for the bundled generator so a checkout on
  another operating system cannot change them.
- What the site owns stays outside the snapshot: content, `_config.yml`, `_data/`, and the
  includes and layouts the lock does not list. Customise there.

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
navigation, anchors, accessibility hooks) and `scripts/check-site.py` (canonical URLs, sitemap,
robots, privacy policy).

```ruby
raise "#{name}: expected one page heading" unless page.css('h1').size == 1
```

- The message is `<page>: <what is wrong>`.
- The check also asserts what must be absent: `scripts`, `docs` and `ANALYTICS.md` must not
  exist in the output.
- Every root-relative image and link inside `main` must point at a file in `_site`, so a renamed
  or deleted image fails the build instead of shipping a broken figure.
- A new site-wide rule is one more assertion in the script that already walks the pages, not a
  new script.

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

## Examples rendered by the library they show

**Problem.** A project page shows charts drawn by the library it describes. A screenshot or a
hand-edited copy would drift from what the library draws, and nobody could make it again.

**Pattern.** A small pinned script renders the examples, and its output is committed. Reference:
`scripts/borrowdale-examples/render.mjs`, which writes `assets/images/projects/borrowdalejs/`.

- The library version is pinned exactly in `package.json`, with a lockfile, so a re-render
  reproduces the committed files byte for byte until the pin is moved on purpose.
- Every file is produced in memory first and written only when all of them succeeded, so a
  failure leaves the committed images as they were.
- Each SVG embeds the font files its labels need, so it looks the same wherever it is opened.
  The script fails if a label uses a character the font does not cover, rather than letting the
  browser substitute another font.
- Each SVG gets a paper-coloured background, because the library draws dark ink on a
  transparent ground that the site's dark theme would hide. It also gets the embedded font's
  licence notice (SIL OFL 1.1), which must travel with every copy of the font.
- The link-preview PNG is the first chart laid out at 600 by 315 and photographed by headless
  Chromium at twice the pixel density.
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

## Embedded code and screenshots

**Problem.** Long code samples and full-size screenshots need to be readable on a narrow screen
and usable from the keyboard, and the source must stay reachable when an embed fails to load.

**Pattern.** Two includes. Reference: `_includes/gist.html`, `_includes/article-image.html`.

```liquid
{% include gist.html id="<account>/<gist id>" %}
{% include article-image.html src="/assets/images/001/dag_docs.png" alt="DAG level docs" %}
```

- The Gist include renders a "View source" link beside the embed, so the code is one click away
  without JavaScript, and wraps the embed in a focusable, labelled scroll region.
- The image include links the image to its full-size file and uses `alt` as the caption unless
  `caption` is given.
- The build fails on a code block in a post that is not keyboard accessible.

## Contents list from headings

**Problem.** Long posts need a table of contents that cannot go stale.

**Pattern.** The post layout derives it from the rendered `<h2 id="…">` elements, and shows it
only when a post has more than three sections. Reference: `_includes/contents.html`. Nothing is
written by hand; the build checks that every entry resolves to exactly one element.
