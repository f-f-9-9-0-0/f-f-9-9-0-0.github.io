import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('privacy_integration', SCRIPTS / 'configure-privacy.py')
privacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(privacy)

class PrivacyIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / 'site'
        self.source.mkdir()
        (self.source / 'index.html').write_text('<html></html>')
        self.env = patch.dict(os.environ, {'CLOUDFLARE_WEB_ANALYTICS_TOKEN': '', 'SITE_OPERATOR_NAME': '', 'PRIVACY_CONTACT_EMAIL': ''})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_jekyll_pages_and_css(self):
        privacy.generate(self.source)
        for lang in ('en', 'hu'):
            for page in ('privacy', 'choices'):
                content = (self.source / 'privacy' / lang / (page + '.html')).read_text()
                self.assertTrue(content.startswith('---\n'))
                self.assertIn('"layout": "privacy"', content)
                self.assertIn('wp-page-' + page, content)
                self.assertIn('"analytics": false', content)
                self.assertIn('"robots": "noindex,nofollow"', content)
            self.assertTrue((self.source / 'privacy' / lang / 'privacy.css').is_file())

    def test_static_preview_ignores_identity(self):
        os.environ['SITE_OPERATOR_NAME'] = 'DO NOT PUBLISH THIS'
        privacy.generate(self.source, static=True)
        content = (self.source / 'privacy/en/privacy.html').read_text()
        self.assertIn('<!doctype html>', content)
        self.assertIn('DRAFT', content)
        self.assertNotIn('DO NOT PUBLISH THIS', content)

    def test_unreviewed_publication_fails_without_writing(self):
        with self.assertRaises(ValueError):
            privacy.generate(self.source, publish=True)
        self.assertFalse((self.source / 'privacy').exists())

    def test_token_cannot_enable_undisclosed_analytics(self):
        os.environ['CLOUDFLARE_WEB_ANALYTICS_TOKEN'] = 'a' * 32
        with self.assertRaises(ValueError):
            privacy.generate(self.source, publish=True)
        self.assertFalse((self.source / 'privacy').exists())

    def test_ads_block_advertising_free_publication(self):
        (self.source / 'index.html').write_text('<script>adsbygoogle</script>')
        with self.assertRaisesRegex(ValueError, 'AdSense'):
            privacy.generate(self.source, publish=True, static=True)

    def test_pinned_snapshot_change_fails(self):
        scripts = Path(self.temp.name) / 'scripts'
        scripts.mkdir()
        shutil.copytree(SCRIPTS / 'privacy-template', scripts / 'privacy-template')
        for name in ('privacy-template.lock.json', 'privacy-site.json'):
            shutil.copyfile(SCRIPTS / name, scripts / name)
        (scripts / 'privacy-template/templates/page.html').write_text('modified')
        with patch.object(privacy, 'HERE', scripts):
            with self.assertRaisesRegex(ValueError, 'snapshot'):
                privacy.generate(self.source)

    def test_reviewed_publication_escapes_liquid_identity(self):
        scripts = Path(self.temp.name) / 'scripts'
        scripts.mkdir()
        shutil.copytree(SCRIPTS / 'privacy-template', scripts / 'privacy-template')
        shutil.copyfile(SCRIPTS / 'privacy-template.lock.json', scripts / 'privacy-template.lock.json')
        config = json.loads((SCRIPTS / 'privacy-site.json').read_text())
        config['publication_reviewed'] = True
        (scripts / 'privacy-site.json').write_text(json.dumps(config))
        os.environ['SITE_OPERATOR_NAME'] = '{{ site.secret }}'
        os.environ['PRIVACY_CONTACT_EMAIL'] = 'privacy@site.test'
        with patch.object(privacy, 'HERE', scripts):
            privacy.generate(self.source, publish=True)
        content = (self.source / 'privacy/en/privacy.html').read_text()
        self.assertNotIn('{{ site.secret }}', content)
        self.assertIn('&#123;&#123; site.secret', content)
        self.assertNotIn('DRAFT', content)

if __name__ == '__main__':
    unittest.main()
