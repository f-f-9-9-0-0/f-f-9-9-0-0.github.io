# Releases

How a change gets from a merged pull request onto the live site, how the pinned bundles are
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

## Refreshing the pinned bundles

Two sets of files are copied from elsewhere and pinned by hash
([`patterns.md`](patterns.md), "Pinned snapshot of shared files"). Neither is edited here.

| Bundle | Files | Lock | Verified by |
|---|---|---|---|
| Presentation (Technical Portfolio starter) | the layouts, includes, stylesheet and image listed in the lock | `scripts/portfolio-template.lock.json` (`version`, `source_commit`, hashes) | `scripts/check-portfolio-template.py`, first step of the build |
| Privacy page generator (`website-privacy`) | `scripts/privacy-template/` | `scripts/privacy-template.lock.json` | `scripts/configure-privacy.py`, before it generates |

### Refreshing the presentation snapshot

1. Make the presentation change in the starter, and note the release and commit to copy from.
2. Copy every file the lock lists from that commit. Copy all of them, not only the ones you
   expect to differ.
3. Update `version`, `source_commit` and each changed hash in the lock, in the same commit.
4. Run `python3 scripts/check-portfolio-template.py`, then the full build and checks.
5. In the pull request, state the version moved from and to, and what a reader will see change.

A file the site needs to differ from the starter does not belong in the snapshot. Move the
difference into a site-owned include, or into `_config.yml`.

### Refreshing the privacy generator

1. Take the files from one reviewed release of the generator.
2. Replace `scripts/privacy-template/` and `scripts/privacy-template.lock.json` together.
3. Update the release named in [`../ANALYTICS.md`](../ANALYTICS.md), "Shared privacy pages".
4. Run the unit tests and `python3 scripts/test-site-build.py`.
5. Read the generated privacy and choices pages in a local preview. A generator release can
   change the wording of a published notice.

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
