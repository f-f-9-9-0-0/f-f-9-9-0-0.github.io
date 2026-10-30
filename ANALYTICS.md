# Analytics and privacy pages

Analytics is disabled by default. Google Analytics is not included in the site templates. Optional Cloudflare Web Analytics uses a public site token, not a Cloudflare API credential.

## Publication setup

Complete `scripts/privacy-site.json` with this website's actual processing information. Set `publication_reviewed` to true only after the inventory and disclosures have been reviewed. Publication also requires the repository secrets `SITE_OPERATOR_NAME` and `PRIVACY_CONTACT_EMAIL`; their values become public in the rendered notice.

Before merging the workflow, select **Settings → Pages → Build and deployment → Source → GitHub Actions**. Legacy branch publishing bypasses the privacy generator and the manual publication gate. Keep the existing site URL/domain configuration. Restrict the `github-pages` environment to `main`.

Pull requests, pushes to `main`, and default manual runs validate draft output without identity or analytics secrets. They cannot publish. To publish, run **Build and deploy GitHub Pages** from `main` and explicitly enable the `deploy` input. Publication requires a successful build and reviewed configuration. No workflow automatically enables Pages or changes its source.

## Optional Cloudflare analytics

Keep analytics mode `off` and the token unset unless activation has been reviewed. The integration has no consent runtime. Automatic beacon activation is supported only with mode `reviewed_exemption`, bilingual descriptions, and a documented applicable `review_reference`. Selecting `consent` does not implement consent and cannot enable the beacon.

For approved activation, add the hostname in Cloudflare Web Analytics, choose manual installation, and save its 32-character hexadecimal site token in the `CLOUDFLARE_WEB_ANALYTICS_TOKEN` repository secret. The token is visible in generated HTML. Do not also enable automatic beacon injection. Empty tokens disable analytics; invalid tokens or mismatched disclosures fail publication.

To disable collection, remove the token, set the disclosure mode to `off`, and publish again. Removing a secret alone does not change files already served to visitors. This integration does not remove historical analytics data or existing browser cookies.

## Shared privacy pages

The generator and templates are bundled from `website-privacy` release `v0.1.0` with SHA-256 integrity checks in `scripts/privacy-template.lock.json`. Refresh the bundle and manifest together from a reviewed release; do not edit bundled templates independently.

The site wrapper generates English and Hungarian privacy and choices pages under `/privacy/<language>/<page>.html`. Drafts use fictional identity, visible draft notices, and `noindex,nofollow`; reviewed publication includes the pages in the sitemap. Each language pair declares reciprocal alternates and self-canonical URLs. Privacy pages never load analytics.

## Build and checks

Use Ruby 3.3 and Python 3. Install dependencies with `bundle install`, then run:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
ANALYTICS_TEMPLATE=./_includes/cloudflare-analytics.html bundle exec ruby scripts/test-analytics.rb
python3 scripts/configure-privacy.py .
python3 scripts/configure-analytics.py ./_data/cloudflare_analytics.json
JEKYLL_ENV=production RUBYOPT=-rlogger bundle exec jekyll build
python3 scripts/check-site.py _site
python3 scripts/test-site-build.py
```

Use a clean source directory for generation. For production output, supply reviewed configuration and the publication environment values, pass `--publish` to the privacy generator, and set `PRIVACY_PUBLISH=true` when checking the output. Never publish draft or synthetic-test artifacts.

After an authorized publication, verify the privacy routes, sitemap, canonical and alternate URLs, HTTPS and 404 responses. Check browser network requests: no Google Analytics requests, no Cloudflare beacon when disabled, and exactly one beacon on eligible pages when enabled. Confirm the correct Cloudflare site receives events. Publishing a notice is not evidence of consent or account-level compliance.

References: [Cloudflare setup](https://developers.cloudflare.com/web-analytics/get-started/), [collection behavior](https://developers.cloudflare.com/web-analytics/data-metrics/data-origin-and-collection/), [GitHub Pages publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
