#!/usr/bin/env python3
"""Build synthetic publication in isolation; never modify the publishable artifact."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def main():
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / 'source'
        output = Path(directory) / 'output'
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(
            '.git', '.bundle', '_site', 'vendor', 'privacy', 'docs', '__pycache__'))
        config_path = source / 'scripts/privacy-site.json'
        config = json.loads(config_path.read_text())
        config['publication_reviewed'] = True
        config['analytics'] = {
            'mode': 'reviewed_exemption',
            'description': {'en': 'Synthetic analytics fixture.'},
            'review_reference': 'Synthetic test record',
        }
        config_path.write_text(json.dumps(config))
        env = dict(os.environ, SITE_OPERATOR_NAME='Test operator',
                   PRIVACY_CONTACT_EMAIL='privacy@site.test',
                   CLOUDFLARE_WEB_ANALYTICS_TOKEN='a' * 32,
                   JEKYLL_ENV='production', RUBYOPT='-rlogger',
                   BUNDLE_GEMFILE=str(ROOT / 'Gemfile'), PRIVACY_PUBLISH='true')
        subprocess.run([sys.executable, str(source / 'scripts/configure-privacy.py'), str(source), '--publish'], env=env, check=True)
        subprocess.run([sys.executable, str(source / 'scripts/configure-analytics.py'), str(source / '_data/cloudflare_analytics.json')], env=env, check=True)
        subprocess.run(['bundle', 'exec', 'jekyll', 'build', '--source', str(source), '--destination', str(output)], cwd=source, env=env, check=True)
        subprocess.run([sys.executable, str(source / 'scripts/check-site.py'), str(output)], env=env, check=True)
        subprocess.run(['bundle', 'exec', 'ruby', str(source / 'scripts/check-design.rb'), str(output)], env=env, check=True)
        spec = importlib.util.spec_from_file_location('site_checks', source / 'scripts/check-site.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.Page(output / 'index.html').beacons == 1, 'Enabled publication must emit exactly one homepage beacon'
        print('Synthetic publication: enabled analytics and bilingual rendered metadata passed')


if __name__ == '__main__':
    main()
