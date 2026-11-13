# Standards

The rules every change to this repository follows. How recurring problems are solved is in
[`patterns.md`](patterns.md); how a merged change reaches the live site is in
[`releases.md`](releases.md). Analytics, the privacy pages and the publication secrets are in
[`../ANALYTICS.md`](../ANALYTICS.md) and are not restated here.

The repository is public and a merge to `main` publishes the website. Read
[Public content](#public-content) before the first commit.

## Posts

### Files and URLs

- A post is `_posts/YYYY-MM-DD-<slug>.md`. The permalink is `/:title/`, so the slug in the file
  name is the URL. **Never rename a published post file**, not even to fix a typo in the slug: the
  old URL would stop resolving, and nothing here redirects.
- The date in the file name and the `date` in the front matter agree.
- A post that is not ready sets `hidden: true`. It still builds, but it is left out of the
  listings and the sitemap.

### Front matter

Every post sets these, in this order:

| Key | Value |
|---|---|
| `title` | The article title, in quotes |
| `layout` | `post` |
| `date` | `YYYY-MM-DD HH:MM` |
| `image` | A photograph under `/assets/images/`. Used for social metadata |
| `illustration` | The topic SVG under `/assets/images/articles/`. Takes priority over `image` in the header and in listings |
| `headerImage` | `true` to show the artwork above the article |
| `tag` | A list. The first tag is shown as the topic in listings |
| `category` | `blog` |
| `author` | A key under `authors` in `_config.yml` |
| `description` | One sentence. It becomes the meta description and the listing summary, and the build fails on a page without one |
| `excerpt_separator` | `<!--more-->` |

A post with `projects: true` is listed on the Projects page as well as in the Blog. A project
that should appear on Projects only is a page instead; see [Project pages](#project-pages).

### Body

- Sections start at `##`. The layout owns the only `<h1>`, and the build fails on a page with
  two.
- A page with more than three `##` sections gets an "On this page" list built from those
  headings. Keep each heading text unique within a post: duplicate headings produce duplicate
  ids, and the build fails on them.
- Name the version a statement was checked against, in an Important callout at the top of the
  post ([`patterns.md`](patterns.md), "Important callout").
- Screenshots go through the `article-image.html` include, with an `alt` that says what the image
  shows. Code longer than a few lines goes through the `gist.html` include.
- Link to versioned documentation where the behaviour is version-specific, not to a "latest" page
  that will drift.
- Links and images inside the site use the `relative_url` filter or a root-relative path.

### Images

- Screenshots and photographs live under `assets/images/<nnn>/`; topic illustrations under
  `assets/images/articles/`, one SVG per post, named after the topic.
- Images for a project page live under `assets/images/projects/<project>/`. Where a script
  generates them, they are never edited by hand: change the script and run it again.
- A screenshot shows no account name, token, internal hostname or other private detail.
- Use only images you have the right to publish.

## Pages and templates

- A page has front matter with `layout`, `title`, `description` and `section`. The five landing
  pages (`/`, `/about/`, `/blog/`, `/projects/`, `/tags/`) each need a description of their own;
  the build compares them.
- `section` must match an entry in `_data/navigation.yml`, which is the single source for the
  main navigation.
- The files listed in `scripts/portfolio-template.lock.json` are a pinned snapshot of the
  Technical Portfolio starter. **Do not edit them here.** A presentation change is made in the
  starter and copied over with an updated lock ([`releases.md`](releases.md), "Refreshing the
  presentation snapshot"). Site-owned files are the content, `_config.yml`, `_data/`, and the
  includes and layouts the lock does not list.
- Everything under `scripts/privacy-template/` is a pinned bundle too, with the same rule and its
  own lock file.
- A root file that is not part of the site is added to `exclude` in `_config.yml`. Jekyll copies
  any other root file into the published site as it is.
- `sitemap.xml` is built from the pages and posts. Do not list URLs in it by hand. A page that
  must stay out sets `sitemap: false`.

### Project pages

A project is described on a page under `projects/`, for example `projects/borrowdalejs.md` at
`/projects/borrowdalejs/`. The Projects page lists every page and post with `projects: true`,
newest first.

| Key | Value |
|---|---|
| `title`, `description` | As for any page |
| `layout` | `page` |
| `section` | `projects`, so the navigation marks Projects |
| `projects` | `true` |
| `permalink` | `/projects/<project>/` |
| `date` | `YYYY-MM-DD HH:MM:SS`, **with seconds**. Without them the value is text, not a date, and the Projects list fails to sort as soon as a project post exists |
| `illustration` | The listing thumbnail |
| `image` | A raster image (PNG or JPEG) for link previews, ideally 1200×630. Most platforms ignore SVG here |
| `tags` | A list. The first is shown as the topic in the listing |
| `seo` | `type: WebPage`, so the structured data does not call the page a blog post |
| `hidden` | `true` keeps it off the Projects page and out of the sitemap while it is drafted |

A project page is not a post. It stays off the Blog list, the home page, the tags page and the
feed, and the page layout adds nothing around its content:

- Wrap the content in `<div class="article-body" markdown="1">` to get the article styles.
- Write code blocks as `<pre tabindex="0" role="region" aria-label="…">`. The post layout adds
  those attributes for posts; on a page they are written by hand, and the build fails without
  them.

## Configuration and secrets

- `_data/cloudflare_analytics.json` is committed with an empty token. The build fills it from a
  repository secret. Never commit a token, although the published HTML does show it.
- The operator name and the privacy contact address come from repository secrets and exist only
  in the published build. They never appear in a committed file, an issue or a pull request.
- `scripts/privacy-site.json` describes the site's actual data processing. Changing it changes a
  published legal notice: set `reviewed_on` to the date of the review, and say in the pull
  request what was reviewed.

## Scripts and checks

- Checks live in `scripts/` and run in the workflow in the order it lists them. A script reads
  the built `_site` (or builds its own temporary copy) and exits non-zero with a message that
  names the page and the problem.
- Python is invoked as `python3`, uses only the standard library, and reads and writes text as
  UTF-8. Paths are resolved from the script's own location.
- The one exception is `scripts/borrowdale-examples/`, a Node.js script (version 22 or later) that
  renders the BorrowdaleJS chart examples. Its dependencies are pinned exactly and locked in
  `package-lock.json`, and its `node_modules/` is ignored. The workflow does not run it: the
  images it writes are committed ([`releases.md`](releases.md), "Re-rendering the project
  charts").
- Unit tests are `scripts/test_*.py`, discovered by `python3 -m unittest`. A test arranges its
  input, acts once and asserts literal values.
- A new rule for the rendered site gets its check in the same pull request, so the next change
  cannot break it unnoticed.
- The bundled files under `scripts/privacy-template/` are checked in with LF line endings
  (`.gitattributes`), because their hashes are pinned.

## Workflow

`.github/workflows/pages.yml` builds every pull request and builds and deploys every push to
`main`. A change to it is a change to what gets published and with which secrets.

- The secrets are passed only when the run is a push to `main` or a manual run from `main` with
  `deploy` enabled. Keep that condition on every step that reads a secret, so a pull request
  build never sees one.
- Only the `deploy` job has `pages: write` and `id-token: write`. The workflow default is
  `contents: read`.
- Actions are pinned to a full commit SHA, with the version in a trailing comment.
- The checkout sets `persist-credentials: false`. Jobs set `timeout-minutes`.
- Steps print no secret and no environment dump.
- The `paths-ignore` lists for `pull_request` and `push` stay identical. A path belongs there only
  if it can never change the built site.

## Documentation

- `README.md` introduces the site. `ANALYTICS.md` covers analytics, the privacy pages and the
  publication setup. `docs/` holds this guide, [`patterns.md`](patterns.md),
  [`releases.md`](releases.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md).
- `docs/`, `README.md` and `ANALYTICS.md` are excluded from the site and from the workflow
  triggers. A new documentation file goes under `docs/`.
- Docs change in the pull request that changes the behaviour they describe.
- State what was measured or checked, with its date, not what is expected to hold.

## Public content

Everything here is world-readable and most of it is permanent: the history, pull requests,
issues, workflow logs and the site.

- No credentials, tokens or `.env` files.
- No machine-specific paths, usernames or hostnames.
- No personal data beyond what the site deliberately publishes. Commit with a GitHub noreply
  address.
- No private working notes, review records or planning documents. A pull request carries the
  source, the checks and the reader-facing docs the change needs, and nothing else.
- Link only to public destinations.

## Git and pull requests

- `main` is the only long-lived branch, and pull requests target it. Nobody pushes to `main`
  directly.
- Branch names are `<scope>/<plain-description>`: `content/` for posts, `site/` for templates,
  styles and site behaviour, `ci/` for the workflow and checks, `docs/` for documentation. For
  example `ci/auto-deploy-pages`.
- Commit subjects are one sentence in the imperative, starting with a capital letter, with no
  full stop and no prefix: `Deploy GitHub Pages on every push to main`. The body says why, when
  the diff does not.
- All commits land before the pull request opens. Every push to an open pull request runs the
  whole workflow again.
- Pull requests are squash-merged, so the title becomes the commit subject on `main`.
- A pull request description states:
  - what changed and why, with `Fixes #N` where it resolves an issue;
  - which pages or URLs change for a reader;
  - which checks ran, locally or in CI, and which did not. A docs-only change runs none in CI.
- Merging a change outside the ignored documentation paths deploys the site. Review the pull
  request as the publication it is.
