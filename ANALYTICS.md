# Cloudflare Web Analytics

Google Analytics has been removed from the site's templates. Cloudflare Web
Analytics is **disabled by default**: the checked-in configuration contains no
token. A normal build without the token sends no analytics to either provider.

## Configure the site token

1. Add the hostname in Cloudflare **Web Analytics**, select manual JavaScript
   installation, and copy the 32-character hexadecimal **site token** from the
   supplied snippet. This is not a Cloudflare API token.
2. In this GitHub repository, open **Settings → Secrets and variables → Actions**
   and add the repository secret `CLOUDFLARE_WEB_ANALYTICS_TOKEN`.
3. Run **Build and deploy GitHub Pages** on `main`, or let a push to `main` run it.
   Pull-request builds deliberately receive no analytics token.

The token is a public identifier and is visible in the resulting HTML/JavaScript.
Using a GitHub secret keeps configuration out of source; it does not make the
published identifier confidential. Empty values disable analytics; malformed
nonempty values fail the build. Each website should have its own Cloudflare token.
Do not enable Cloudflare's automatic beacon injection alongside this manual
integration, otherwise analytics may be counted twice.

## GitHub Pages deployment

Change **Settings → Pages → Build and deployment → Source** from “Deploy from a
branch” to **GitHub Actions** when adopting this workflow. Legacy Pages Jekyll
builds cannot read repository secrets. The workflow builds pull requests without
deploying, and deploys successful `main` builds to the `github-pages` environment.
No Pages settings are changed by this PR itself. Preserve the existing domain.

## Build outside Actions

Set `CLOUDFLARE_WEB_ANALYTICS_TOKEN` in the build environment, then run from the
repository root:

```sh
python3 scripts/configure-analytics.py ./_data/cloudflare_analytics.json
JEKYLL_ENV=production bundle exec jekyll build
```

Do not commit generated token configuration. To disable collection, remove the
secret/environment variable and rebuild/redeploy; removing a secret alone does
not alter already deployed static files. Remove the secret before rebuilding to
reset generated configuration to its empty default.

## Privacy and rollout

Cloudflare says Web Analytics uses no cookies, localStorage, or visitor
fingerprinting, and does not track individual users across customers' sites.
This is not a declaration that the whole website is GDPR compliant or that every
jurisdiction exempts every analytics beacon from consent. Before enabling the
token, review the site's privacy notice, applicable legal basis/ePrivacy rules,
Cloudflare processing/transfer terms, and collection settings. Manual snippet
installation does not implement Cloudflare's proxy-side EU visitor exclusion.
Avoid personal data in page paths and review other embedded third-party services.

After publishing, verify in browser Network tools that there are no GA requests,
and (with a token) exactly one Cloudflare beacon script. Confirm visits reach the
correct Cloudflare site. Test without a token too: there must be no Cloudflare
beacon requests. Historical GA data and browser cookies are not deleted by this
source change; the removed GA code no longer reads or refreshes them.

References:
- https://developers.cloudflare.com/web-analytics/get-started/
- https://www.cloudflare.com/web-analytics/
- https://developers.cloudflare.com/web-analytics/data-metrics/data-origin-and-collection/

## Checks

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
BUNDLE_GEMFILE=./Gemfile ANALYTICS_TEMPLATE=./_includes/cloudflare-analytics.html bundle exec ruby scripts/test-analytics.rb
```
