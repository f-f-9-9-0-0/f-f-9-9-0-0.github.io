import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("configure-analytics.py")

class AnalyticsConfigTests(unittest.TestCase):
    def configure(self, token):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "analytics.json"
            env = dict(os.environ)
            env.pop("CLOUDFLARE_WEB_ANALYTICS_TOKEN", None)
            if token is not None:
                env["CLOUDFLARE_WEB_ANALYTICS_TOKEN"] = token
            result = subprocess.run([sys.executable, str(SCRIPT), str(output)], env=env,
                                    capture_output=True, text=True)
            return result, json.loads(output.read_text()) if output.exists() else None

    def test_missing_empty_and_whitespace_disable(self):
        for token in [None, "", "  "]:
            with self.subTest(token=token):
                result, config = self.configure(token)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(config, {"token": ""})

    def test_site_token_is_preserved_without_logging(self):
        token = "0123456789abcdef0123456789abcdef"
        result, config = self.configure("  " + token + "  ")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(config, {"token": token})
        self.assertNotIn(token, result.stdout + result.stderr)

    def test_invalid_values_fail_before_writing(self):
        for token in ["placeholder", "G-1234567890", "a" * 31, "g" * 32, "</script>"]:
            with self.subTest(token=token):
                result, config = self.configure(token)
                self.assertNotEqual(result.returncode, 0)
                self.assertIsNone(config)

if __name__ == "__main__":
    unittest.main()
