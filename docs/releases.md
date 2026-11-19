# Releases

How a change gets from a merged pull request onto the live site, how the pinned files are
refreshed, and how to roll back.

This repository cuts no tags and keeps no release notes. A release here is **a merge to `main`
whose `Build and deploy GitHub Pages` run succeeded**. The record is the merged pull request and
that run.

## Merging publishes

| Change | What it takes to be live |
|---|---|
| A post, page, layout, include, style, image, `_config.yml`, `_data/`, anything under `scripts/`, the workflow | The merge. The push to `main` builds with the publication secrets and deploys when every check passes |
| Only `README.md`, `ANALYTICS.md` or files under `docs/` | Nothing to deploy. The push starts no run, and the site is unchanged |
| A repository secret or a Pages setting | A new deploy. Changing a secret alone does not change the files already served |

There is no staging site. The pull request build is the rehearsal: it runs every check on a
draft build, without the secrets.

A failed build deploys nothing, and the previous site stays up.

## Before the merge

1. The pull request build is green. For a change the workflow ignores, say in the pull request
   which checks ran locally ([`../ANALYTICS.md`](../ANALYTICS.md), "Build and checks").
2. The pull request names the pages or URLs that change for a reader.
3. For a post: the file name is final (it is the URL), the description is set, and the post was
   read in a local preview at a narrow and a wide width.
4. For a change to `scripts/privacy-site.json`: the disclosure was reviewed, `reviewed_on` is
   updated, and the pull request says what was reviewed. The published notice is a legal text.
5. For a change to the workflow: the draft and published conditions still match on every step
   that reads a secret ([`patterns.md`](patterns.md), "One build, draft or published").

To preview locally, with Ruby 3.3:

```sh
bundle install
python3 scripts/configure-privacy.py .
bundle exec jekyll serve --config _config.yml,_config_development.yml
```

The generator refuses to run when `privacy/` already exists; delete that directory first.

## After the merge

1. Watch the run for the merge commit:

   ```sh
   gh run list --workflow pages.yml --branch main --limit 5
   ```

2. When the `deploy` job is green, open the changed pages on the live site. Allow a few minutes
   for caches.
3. For a change to analytics, the privacy pages or the workflow, do the post-publication checks
   in [`../ANALYTICS.md`](../ANALYTICS.md), "Build and checks": the privacy routes, the sitemap,
   canonical URLs, and the network requests the page makes.
4. Record the run on the issue the pull request fixed, if there is one. `Fixes #N` closes the
   issue at merge, which is before the deploy finishes: reopen it if the deploy fails or the
   check on the live page does.

## What is live now

The last successful run on `main` is the deployed revision:

```sh
gh run list --workflow pages.yml --branch main --status success --limit 1 --json headSha,updatedAt,event,url
```

The tip of `main` can be ahead of it by documentation-only commits, which start no run.

## Redeploying without a commit

Run **Build and deploy GitHub Pages** from `main` with the `deploy` input enabled. Use it after
changing a repository secret, or to rebuild with current dependencies. A manual run without
`deploy`, or from another branch, validates a draft build and publishes nothing.

The gem versions are not locked in the repository (`Gemfile.lock` is not committed), so a
redeploy can pick up newer gems than the last run used. If the output changes with no commit
behind it, compare the "Install site dependencies" logs of the two runs.

## Refreshing the pinned files

Three sets of files come from pinned releases elsewhere. None is edited here.

| Files | Pinned in | Refreshed by |
|---|---|---|
| The privacy page generator (`website-privacy`), `scripts/privacy-template/` | `scripts/privacy-template.lock.json`, verified by `scripts/configure-privacy.py` before it generates | "Refreshing the privacy generator" |
| The drawings under `assets/images/` | the `@borrowdale` versions in `scripts/site-assets/package.json` | "Re-rendering the drawings" |
| The fonts, `assets/fonts/` and `assets/css/fonts.css` | the `@fontsource` versions in `scripts/site-assets/package.json` | "Refreshing the fonts" |

The scripts in `scripts/site-assets/` need Node.js 22 or later. Where the installed Node is older,
`npx -p node@22 -- npm …` runs them on Node 22 without changing it.

### Refreshing the privacy generator

1. Take the files from one reviewed release of the generator.
2. Replace `scripts/privacy-template/` and `scripts/privacy-template.lock.json` together.
3. Update the release named in [`../ANALYTICS.md`](../ANALYTICS.md), "Shared privacy pages".
4. Run the unit tests and `python3 scripts/test-site-build.py`.
5. Read the generated privacy and choices pages in a local preview. A generator release can
   change the wording of a published notice.

### Re-rendering the drawings

The chart examples on the BorrowdaleJS page, the home page hero and the topic illustrations are
rendered by `scripts/site-assets/render.mjs`, pinned to one release of the library. A new library
release changes nothing on the site until the pin is moved. Re-render also after changing a colour
in `_data/palette.json`: the drawings carry the palette's values, and the build fails on a drawing
whose colours no longer match it.

1. In `scripts/site-assets/`, set the new version of each `@borrowdale` package in `package.json`,
   then run `npm install` to update the lockfile. For a colour change only, run `npm ci`.
2. Run `npx playwright-core install chromium` once, then `npm run render`. It fails, and writes
   nothing, if a spec no longer validates or a label uses a character the font lacks.
3. Review the image diff, and read the pages in a local preview, in light and in dark mode and at a
   phone width. The drawings may change between library versions.
4. Check that the code sample on the BorrowdaleJS page still matches the first chart's spec.

The workflow does not run the script, so the committed images are what is published.

### Refreshing the fonts

1. In `scripts/site-assets/`, set the new version of each `@fontsource` package in `package.json`,
   then run `npm install`.
2. Run `npm run fonts`. It fails, and writes nothing, if a face it copies is missing from a
   package.
3. Read a post and the home page in a local preview, and compare the file list and licences in
   `assets/fonts/` with the previous commit.

### Actions and Ruby

- Actions in `pages.yml` are pinned to a commit SHA. To move one, replace the SHA and the
  version comment together, and read the action's release notes first: the build job handles the
  publication secrets, and the deploy job can write to Pages.
- The Ruby and Bundler versions are set in `pages.yml`. Change them there and in
  [`../ANALYTICS.md`](../ANALYTICS.md) in the same pull request.

## Rolling back

Revert the pull request and merge the revert. The merge deploys the previous content like any
other change. A revert that is merged but whose run failed has rolled nothing back.

What a rollback does not undo:

- Pages already cached or indexed stay visible elsewhere for a while.
- A post URL that was live and is removed returns the 404 page. Prefer correcting a published
  post to removing it.
- Analytics data already collected is not removed by disabling the beacon
  ([`../ANALYTICS.md`](../ANALYTICS.md), "Cloudflare analytics").
- A value that was published by mistake is public. If it was a credential, revoke it first, then
  fix the site.
