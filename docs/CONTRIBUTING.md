# Contributing

This is the source of a personal website: technical articles on data engineering, built with
Jekyll and published with GitHub Pages. Corrections are welcome: a wrong statement, an example
that no longer runs, a broken link, a typo, or a layout or accessibility problem.

New articles are written by the site's author. If you have a topic to suggest, open an issue.

## Report a problem

[Open an issue](https://github.com/f-f-9-9-0-0/f-f-9-9-0-0.github.io/issues/new) and include:

- the address of the page;
- what is wrong, and what you expected;
- for a technical error: the tool version you used, and the smallest example that shows it;
- for a display problem: the browser, and the window width or device.

Remove private data and credentials from anything you paste.

## Propose a change

Small fixes can go straight to a pull request. For anything larger (restructuring an article,
changing a layout or a build check), describe it in an issue first.

### Set up

You need Ruby 3.3 and Python 3.

```sh
bundle install
python3 scripts/configure-privacy.py .
bundle exec jekyll serve --config _config.yml,_config_development.yml
```

The site is then at `http://127.0.0.1:4000`. The second command generates draft privacy pages
into `privacy/`, which git ignores; delete that directory before running it again.

### Where things are

| Path | What it holds |
|---|---|
| `_posts/` | The articles, one Markdown file each |
| `projects/` | The project pages, one Markdown file each |
| `assets/images/` | Screenshots, photographs, the topic illustrations, the home page hero, and the images of project pages under `projects/` |
| `_layouts/`, `_includes/`, `assets/css/site.css` | The presentation |
| `_data/palette.json` | The light and dark colours, by name |
| `assets/fonts/`, `assets/css/fonts.css` | The self-hosted fonts and their licences, written by a script |
| `_config.yml`, `_data/` | Site settings and navigation |
| `scripts/` | The build checks, the privacy page generator and their tests |
| `scripts/site-assets/` | The scripts that render the BorrowdaleJS drawings and copy the fonts. Run them with Node.js 22 or later: `npm ci`, `npx playwright-core install chromium`, then `npm run render` or `npm run fonts` |
| `.github/workflows/pages.yml` | The build and deployment |
| `docs/` | These guides |

### Rules for a change

The full list is in [`standards.md`](standards.md). The ones that catch most first changes:

- Do not rename a published post file. Its name is its address.
- Do not edit anything under `scripts/privacy-template/`. It is pinned by hash and the build fails
  when it changes.
- Do not edit the drawings, the fonts or `assets/css/fonts.css` by hand. Change the script that
  writes them and run it again.
- Use the colour names from `_data/palette.json`, never a colour value, and check a change in both
  light and dark mode.
- Start sections in a post at `##`, and give screenshots a meaningful `alt` text.
- Say which version of a tool a correction was checked against.

### Check it

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
JEKYLL_ENV=production RUBYOPT=-rlogger bundle exec jekyll build
python3 scripts/check-site.py _site
bundle exec ruby scripts/check-design.rb _site
```

The same checks run on every pull request, except for one that changes only documentation. The
complete sequence, including the analytics tests, is in
[`../ANALYTICS.md`](../ANALYTICS.md), "Build and checks".

## Commits and pull requests

- Branch from `main` and open the pull request against `main`. Name the branch
  `<scope>/<plain-description>`, with `content`, `site`, `ci` or `docs` as the scope.
- Write commit subjects as one imperative sentence, for example
  `Fix the catchup example in the unpausing article`.
- Keep a pull request to one change, and finish it before opening: each further push runs the
  whole build again.
- In the description, say what changed and why, which pages are affected, and which checks you
  ran.
- Pull requests from outside the project may wait for a maintainer to approve their workflow
  run. The maintainer merges, and a merge publishes the site
  ([`releases.md`](releases.md)).

## What not to commit

Credentials or tokens, `.env` files, machine-specific paths, personal data, the built `_site/`
and `privacy/` directories, and private working notes. Screenshots must not show account names,
tokens or internal addresses.

## Licence

The presentation is maintained in this repository. [`../LICENSE-portfolio`](../LICENSE-portfolio)
covers the template code it started from, which remains in some layouts and includes, and
[`../README.md`](../README.md) names the older components it derives from. The fonts' licences are
in `assets/fonts/`. No licence is stated for the articles and their
images: ask before reusing them. Material you add from elsewhere needs a licence that allows
publishing it here, and its source named.
