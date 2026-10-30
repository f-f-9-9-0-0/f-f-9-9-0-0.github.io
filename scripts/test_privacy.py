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
        self.scripts = Path(self.temp.name) / 'scripts'
        self.scripts.mkdir()
        shutil.copytree(SCRIPTS / 'privacy-template', self.scripts / 'privacy-template')
        shutil.copyfile(SCRIPTS / 'privacy-template.lock.json', self.scripts / 'privacy-template.lock.json')
        self.config = json.loads((SCRIPTS / 'privacy-site.json').read_text())
        self.config['analytics'] = {'mode': 'off'}
        self.config['publication_reviewed'] = False
        self.write_config()
        here = patch.object(privacy, 'HERE', self.scripts)
        here.start()
        self.addCleanup(here.stop)
        self.env = patch.dict(os.environ, {'CLOUDFLARE_WEB_ANALYTICS_TOKEN': '', 'SITE_OPERATOR_NAME': '', 'PRIVACY_CONTACT_EMAIL': ''})
        self.env.start()
        self.addCleanup(self.env.stop)

    def write_config(self):
        (self.scripts / 'privacy-site.json').write_text(json.dumps(self.config))

    def publication_identity(self):
        os.environ['SITE_OPERATOR_NAME'] = 'Test operator'
        os.environ['PRIVACY_CONTACT_EMAIL'] = 'privacy@site.test'

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
                metadata = json.loads(content.split('---')[1])
                self.assertEqual(set(metadata['alternates']), {'en', 'hu'})
                self.assertEqual(metadata['alternates'][lang], metadata['permalink'])
                self.assertTrue(metadata['description'])
            self.assertTrue((self.source / 'privacy' / lang / 'privacy.css').is_file())

    def test_static_preview_ignores_identity(self):
        os.environ['SITE_OPERATOR_NAME'] = 'DO NOT PUBLISH THIS'
        privacy.generate(self.source, static=True)
        content = (self.source / 'privacy/en/privacy.html').read_text()
        self.assertIn('<!doctype html>', content)
        self.assertIn('DRAFT', content)
        self.assertNotIn('DO NOT PUBLISH THIS', content)

    def test_unreviewed_publication_fails_without_writing(self):
        self.publication_identity()
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
        (self.scripts / 'privacy-template/templates/page.html').write_text('modified')
        with self.assertRaisesRegex(ValueError, 'snapshot'):
            privacy.generate(self.source)

    def test_reviewed_publication_escapes_liquid_identity(self):
        self.config['publication_reviewed'] = True
        self.write_config()
        self.publication_identity()
        os.environ['SITE_OPERATOR_NAME'] = '{{ site.secret }}'
        privacy.generate(self.source, publish=True)
        content = (self.source / 'privacy/en/privacy.html').read_text()
        self.assertNotIn('{{ site.secret }}', content)
        self.assertIn('&#123;&#123; site.secret', content)
        self.assertNotIn('DRAFT', content)
        metadata = json.loads(content.split('---')[1])
        self.assertTrue(metadata['sitemap'])
        self.assertEqual(metadata['robots'], 'index,follow')

    def test_reviewed_exemption_with_token_publishes(self):
        self.config['publication_reviewed'] = True
        self.config['analytics'] = {
            'mode': 'reviewed_exemption',
            'description': {'en': 'Synthetic analytics fixture.', 'hu': 'Szintetikus teszt.'},
            'review_reference': 'Synthetic test record',
        }
        self.write_config()
        self.publication_identity()
        os.environ['CLOUDFLARE_WEB_ANALYTICS_TOKEN'] = 'a' * 32
        privacy.generate(self.source, publish=True)
        content = (self.source / 'privacy/en/choices.html').read_text()
        self.assertIn('Synthetic analytics fixture.', content)
        self.assertNotIn('DRAFT', content)

    def test_reviewed_exemption_without_token_is_rejected(self):
        self.config['analytics'] = {'mode': 'reviewed_exemption'}
        self.write_config()
        with self.assertRaisesRegex(ValueError, 'disabled runtime'):
            privacy.generate(self.source, publish=True)
        self.assertFalse((self.source / 'privacy').exists())

if __name__ == '__main__':
    unittest.main()
