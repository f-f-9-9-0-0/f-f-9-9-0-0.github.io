#!/usr/bin/env python3
"""Generate reviewed privacy pages with the pinned shared generator."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile

HERE = Path(__file__).resolve().parent

def generate(source, publish=False, static=False):
    source = Path(source)
    config = json.loads((HERE / 'privacy-site.json').read_text())
    lock = json.loads((HERE / 'privacy-template.lock.json').read_text())
    tool = HERE / 'privacy-template'
    for name, digest in lock['files'].items():
        if hashlib.sha256((tool / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Shared template snapshot differs from its pinned manifest')
    token = os.environ.get('CLOUDFLARE_WEB_ANALYTICS_TOKEN', '').strip()
    mode = config['analytics']['mode']
    if token and (not publish or mode != 'reviewed_exemption'):
        raise ValueError('A token requires publication and a documented exemption; consent runtime is not implemented')
    if publish and mode != 'off' and not token:
        raise ValueError('Analytics disclosure does not match disabled runtime')
    if publish and static and 'adsbygoogle' in (source / 'index.html').read_text():
        raise ValueError('Remove AdSense before publishing the planned advertising-free notice')
    spec = importlib.util.spec_from_file_location('shared_privacy', tool / 'build.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    destination = source / 'privacy'
    if destination.exists():
        raise ValueError('Generated privacy directory already exists; use a clean build')
    with tempfile.TemporaryDirectory() as temp:
        rendered = Path(temp) / 'rendered'
        module.build(config, rendered, publish=publish, fragment=not static)
        if not static:
            for language in config['languages']:
                for page in ('privacy', 'choices'):
                    path = rendered / language / (page + '.html')
                    # Prevent literal Liquid syntax in public identity/text being executed by Jekyll.
                    body = path.read_text().replace('{', '&#123;').replace('}', '&#125;')
                    title = {'en': {'privacy': 'Privacy notice', 'choices': 'Privacy choices'},
                             'hu': {'privacy': 'Adatkezelési tájékoztató', 'choices': 'Adatvédelmi beállítások'}}[language][page]
                    metadata = {'layout': 'privacy', 'title': title, 'lang': language,
                                'permalink': '/privacy/' + language + '/' + page + '.html',
                                'analytics': False, 'comments': False, 'sitemap': publish,
                                'robots': 'index,follow' if publish else 'noindex,nofollow'}
                    # JSON is valid YAML; one mapping between front matter delimiters.
                    path.write_text('---\n' + json.dumps(metadata, ensure_ascii=False) + '\n---\n' + body)
        shutil.copytree(rendered, destination)
    print('Privacy pages generated: ' + ('reviewed publication' if publish else 'draft preview'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--static', action='store_true')
    args = parser.parse_args()
    generate(args.source, args.publish, args.static)
