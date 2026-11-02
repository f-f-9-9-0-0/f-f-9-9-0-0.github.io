#!/usr/bin/env python3
"""Check built canonical URLs, bilingual privacy metadata and publication policy."""
import argparse
from html.parser import HTMLParser
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.lang = None
        self.canonicals = []
        self.alternates = {}
        self.robots = None
        self.description = None
        self.beacons = 0
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.lang = attrs.get('lang')
        if tag == 'link':
            if attrs.get('rel') == 'canonical':
                self.canonicals.append(attrs.get('href'))
            if attrs.get('rel') == 'alternate' and 'hreflang' in attrs:
                self.alternates[attrs['hreflang']] = attrs.get('href')
        if tag == 'meta' and attrs.get('name') == 'robots':
            self.robots = attrs.get('content')
        if tag == 'meta' and attrs.get('name') == 'description':
            self.description = attrs.get('content')
        if tag == 'script' and attrs.get('src') == 'https://static.cloudflareinsights.com/beacon.min.js':
            self.beacons += 1


def check(root, published, origin):
    root = Path(root)
    origin = origin.rstrip('/')
    home = Page(root / 'index.html')
    assert home.canonicals == [origin + '/'], 'Homepage canonical does not match the site root'
    urls = [item.text for item in ET.parse(root / 'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    assert len(urls) == len(set(urls)), 'Duplicate sitemap URLs'
    assert origin + '/' in urls, 'Homepage is missing from sitemap'
    for url in urls:
        assert url.startswith(origin + '/'), 'Sitemap contains another origin'
        path = urlsplit(url).path
        assert '//' not in path, 'Sitemap contains a doubled slash'
        assert path != '/404.html', '404 page must not be in sitemap'
        target = root / path.lstrip('/')
        if path.endswith('/'):
            target /= 'index.html'
        assert target.is_file(), 'Sitemap points to a missing file: ' + path
    for language in ('en',):
        for kind in ('privacy', 'choices'):
            path = '/privacy/' + language + '/' + kind + '.html'
            page = Page(root / path.lstrip('/'))
            assert page.lang == language, 'Document language does not match content'
            assert page.canonicals == [origin + path], 'Privacy canonical mismatch'
            expected = {lang: origin + '/privacy/' + lang + '/' + kind + '.html' for lang in ('en',)}
            assert page.alternates == expected, 'Language alternates must include self and counterpart'
            assert page.description, 'Missing privacy description'
            assert page.robots == ('index,follow' if published else 'noindex,nofollow'), 'Wrong privacy indexing policy'
            assert ((origin + path) in urls) == published, 'Sitemap disagrees with privacy publication status'
            assert page.beacons == 0, 'Privacy pages must not load analytics'
    assert 'Sitemap: ' + origin + '/sitemap.xml' in (root / 'robots.txt').read_text()
    assert Page(root / '404.html').robots == 'noindex,follow'
    for name in ('scripts', 'docs', 'ANALYTICS.md'):
        assert not (root / name).exists(), 'Non-site material included in output: ' + name
    print('Built website: canonical URLs, language alternates, sitemap, robots and privacy analytics policy passed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    config = json.loads(Path(__file__).with_name('privacy-site.json').read_text())
    check(args.output, os.environ.get('PRIVACY_PUBLISH') == 'true', config['site_url'])
